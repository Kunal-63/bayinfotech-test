"""Chat API endpoint."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
import uuid
from datetime import datetime

from app.models.schemas import ChatRequest, ChatResponse, KBReference, GuardrailInfo
from app.models.database import Conversation, Message, GuardrailEvent, Ticket
from app.models.enums import Tier, Severity
from app.services.guardrail_service import GuardrailService
from app.services.tier_service import TierService
from app.services.rag_service import RAGService
from app.utils.db import get_db
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Initialize services
guardrail_service = GuardrailService()
tier_service = TierService()
rag_service = RAGService()

# Namespace for generating UUIDs from session IDs
SESSION_NAMESPACE = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')


def _session_id_to_uuid(session_id: str) -> str:
    """Convert session_id string to deterministic UUID string."""
    try:
        # Try to parse as UUID first
        uuid.UUID(session_id)
        return session_id
    except ValueError:
        # Generate deterministic UUID from string using uuid5
        return str(uuid.uuid5(SESSION_NAMESPACE, session_id))


def _create_ticket(db: Session, request: ChatRequest, tier: Tier, severity: Severity, answer: str) -> str:
    """Create a support ticket for escalated issues."""
    try:
        # Generate ticket ID
        ticket_count = db.query(Ticket).count()
        ticket_id = f"TICKET-{ticket_count + 1:04d}"
        
        # Create ticket
        ticket = Ticket(
            id=ticket_id,
            session_id=_session_id_to_uuid(request.session_id),
            subject=f"Escalated Chat: {request.message[:50]}...",
            description=f"User Message: {request.message}\n\nAI Response: {answer}",
            tier=tier.value,
            severity=severity.value,
            status="OPEN",
            user_role=request.user_role.value,
            context=request.context.model_dump(),
            ai_analysis=f"Escalated due to severity {severity.value} or repeated failure."
        )
        
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        
        logger.info("auto_ticket_created", ticket_id=ticket_id)
        return ticket_id
    except Exception as e:
        logger.error("auto_ticket_creation_failed", error=str(e))
        return None


def _get_conversation_history(db: Session, conversation_id: str) -> List[Dict[str, str]]:
    """Get recent conversation history for context."""
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.desc()).limit(10).all()
    
    # Reverse to get chronological order
    messages = list(reversed(messages))
    
    history = []
    for msg in messages:
        history.append({
            "role": msg.role,
            "content": msg.content
        })
    
    return history


def _check_repeated_failure(conversation_history: List[Dict[str, str]], current_message: str) -> bool:
    """Check if this is a repeated failure (similar message asked multiple times)."""
    if len(conversation_history) < 2:
        return False
    
    # Get last 3 user messages
    user_messages = [msg["content"] for msg in conversation_history if msg["role"] == "user"]
    recent_messages = user_messages[-3:] if len(user_messages) >= 3 else user_messages
    
    current_lower = current_message.lower()
    
    # Check for explicit failure keywords
    failure_keywords = [
        "still fails", "still failing", "still not working", "doesn't work",
        "tried again", "tried multiple times", "3 times", "three times",
        "same error", "persists", "not resolved"
    ]
    
    if any(keyword in current_lower for keyword in failure_keywords):
        return True
    
    # Check for semantic overlap with recent messages
    for msg in recent_messages:
        msg_lower = msg.lower()
        
        # Check for keyword overlap
        current_words = set(current_lower.split())
        recent_words = set(msg_lower.split())
        
        if not current_words or not recent_words:
            continue
            
        overlap = len(current_words & recent_words) / len(current_words | recent_words)
        if overlap > 0.6:
            return True
            
    return False


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Main chat endpoint for AI Help Desk.
    
    Workflow:
    1. Validate request
    2. Check guardrails
    3. If blocked -> return safe response
    4. Retrieve conversation history
    5. Execute RAG pipeline
    6. Classify tier and severity
    7. Save conversation turn
    8. Return response
    """
    logger.info("chat_request_received",
               session_id=request.session_id,
               user_role=request.user_role.value,
               message_preview=request.message[:100])
    
    try:
        # Step 1: Check guardrails
        is_blocked, trigger_type, severity, reason = guardrail_service.check_guardrails(request.message)
        
        if is_blocked:
            # Log guardrail event
            guardrail_event = GuardrailEvent(
                session_id=_session_id_to_uuid(request.session_id),
                trigger_type=trigger_type.value,
                severity=severity.value,
                user_message=request.message
            )
            db.add(guardrail_event)
            db.commit()
            
            logger.warning("guardrail_blocked_request",
                          session_id=request.session_id,
                          trigger_type=trigger_type.value,
                          severity=severity.value)
            
            # Return blocked response
            safe_response = guardrail_service.get_safe_response(trigger_type, reason)
            
            return ChatResponse(
                answer=safe_response,
                kb_references=[],
                confidence=0.0,
                tier=Tier.TIER_3,  # Auto-escalate guardrail violations
                severity=severity,
                needs_escalation=True,
                guardrail=GuardrailInfo(blocked=True, reason=reason),
                ticket_id=None
            )
        
        # Step 2: Get or create conversation
        conversation = db.query(Conversation).filter(
            Conversation.session_id == _session_id_to_uuid(request.session_id)
        ).first()
        
        if not conversation:
            conversation = Conversation(
                session_id=_session_id_to_uuid(request.session_id),
                user_role=request.user_role.value,
                context=request.context.model_dump()
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        # Step 3: Get conversation history
        conversation_history = _get_conversation_history(db, conversation.id)
        
        # Step 4: Execute RAG pipeline
        answer, kb_references, confidence, has_kb_coverage = await rag_service.retrieve_and_generate(
            user_message=request.message,
            db=db,
            conversation_history=conversation_history
        )
        
        # Step 5: Classify tier and severity
        tier, severity, needs_escalation = tier_service.classify_tier_and_severity(
            message=request.message,
            user_role=request.user_role,
            context=request.context.model_dump(),
            kb_coverage=has_kb_coverage,
            repeated_failure=_check_repeated_failure(conversation_history, request.message)
        )
        
        # Step 5.5: Create ticket if escalation needed
        ticket_id = None
        if needs_escalation:
            ticket_id = _create_ticket(db, request, tier, severity, answer)
            # Append ticket info to answer
            if ticket_id:
                answer += f"\n\nI have created a support ticket ({ticket_id}) for this issue. A support engineer will review it shortly."
        
        # Step 6: Save user message
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message,
            tier=tier.value,
            severity=severity.value
        )
        db.add(user_message)
        
        # Step 7: Save assistant response
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=answer,
            kb_references=kb_references,
            confidence=confidence,
            tier=tier.value,
            severity=severity.value,
            guardrail_blocked=False
        )
        db.add(assistant_message)
        db.commit()
        
        logger.info("chat_response_generated",
                   session_id=request.session_id,
                   tier=tier.value,
                   severity=severity.value,
                   confidence=confidence,
                   needs_escalation=needs_escalation)
        
        # Step 8: Return response
        return ChatResponse(
            answer=answer,
            kb_references=kb_references,
            confidence=confidence,
            tier=tier,
            severity=severity,
            needs_escalation=needs_escalation,
            guardrail=GuardrailInfo(blocked=False, reason=None),
            ticket_id=ticket_id
        )
        
    except Exception as e:
        logger.error("chat_request_failed",
                    session_id=request.session_id,
                    error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
