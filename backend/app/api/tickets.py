"""Tickets API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from app.models.schemas import TicketCreate, TicketResponse, TicketUpdate
from app.models.database import Ticket
from app.utils.db import get_db
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

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


@router.post("/tickets", response_model=TicketResponse, status_code=201)
async def create_ticket(ticket_data: TicketCreate, db: Session = Depends(get_db)):
    """Create a new support ticket."""
    try:
        # Generate ticket ID
        ticket_count = db.query(Ticket).count()
        ticket_id = f"TICKET-{ticket_count + 1:04d}"
        
        # Create ticket
        ticket = Ticket(
            id=ticket_id,
            session_id=_session_id_to_uuid(ticket_data.session_id),
            subject=ticket_data.subject,
            description=ticket_data.description,
            tier=ticket_data.tier.value,
            severity=ticket_data.severity.value,
            status="OPEN",
            user_role=ticket_data.user_role.value,
            context=ticket_data.context,
            ai_analysis=ticket_data.ai_analysis
        )
        
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        
        logger.info("ticket_created",
                   ticket_id=ticket_id,
                   tier=ticket_data.tier.value,
                   severity=ticket_data.severity.value)
        
        return ticket
        
    except Exception as e:
        logger.error("ticket_creation_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create ticket")


@router.get("/tickets", response_model=List[TicketResponse])
async def list_tickets(
    status: str = None,
    tier: str = None,
    severity: str = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List tickets with optional filters."""
    try:
        query = db.query(Ticket)
        
        if status:
            query = query.filter(Ticket.status == status)
        if tier:
            query = query.filter(Ticket.tier == tier)
        if severity:
            query = query.filter(Ticket.severity == severity)
        
        tickets = query.order_by(Ticket.created_at.desc()).limit(limit).all()
        
        logger.info("tickets_listed", count=len(tickets))
        
        return tickets
        
    except Exception as e:
        logger.error("ticket_listing_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list tickets")


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    """Get a specific ticket by ID."""
    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        logger.info("ticket_retrieved", ticket_id=ticket_id)
        
        return ticket
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("ticket_retrieval_failed", ticket_id=ticket_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve ticket")


@router.patch("/tickets/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: str,
    update_data: TicketUpdate,
    db: Session = Depends(get_db)
):
    """Update a ticket's status, tier, or severity."""
    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Update fields if provided
        if update_data.status:
            ticket.status = update_data.status.value
        if update_data.tier:
            ticket.tier = update_data.tier.value
        if update_data.severity:
            ticket.severity = update_data.severity.value
        
        ticket.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(ticket)
        
        logger.info("ticket_updated",
                   ticket_id=ticket_id,
                   status=ticket.status,
                   tier=ticket.tier,
                   severity=ticket.severity)
        
        return ticket
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("ticket_update_failed", ticket_id=ticket_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update ticket")
