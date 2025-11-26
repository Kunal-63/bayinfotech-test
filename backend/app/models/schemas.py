"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models.enums import UserRole, Tier, Severity, TicketStatus


# Chat API Schemas
class ChatContext(BaseModel):
    """Context information for chat request."""
    module: Optional[str] = None
    channel: Optional[str] = None


class ChatRequest(BaseModel):
    """Request schema for /api/chat endpoint."""
    session_id: str = Field(..., description="Unique session identifier")
    message: str = Field(..., min_length=1, description="User message")
    user_role: UserRole = Field(..., description="User role")
    context: ChatContext = Field(default_factory=ChatContext, description="Additional context")


class KBReference(BaseModel):
    """Knowledge base reference."""
    id: str
    title: str
    excerpt: Optional[str] = None


class GuardrailInfo(BaseModel):
    """Guardrail activation information."""
    blocked: bool
    reason: Optional[str] = None


class ChatResponse(BaseModel):
    """Response schema for /api/chat endpoint."""
    answer: str
    kb_references: List[KBReference] = []
    confidence: float
    tier: Tier
    severity: Severity
    needs_escalation: bool
    guardrail: GuardrailInfo
    ticket_id: Optional[str] = None


# Ticket API Schemas
class TicketCreate(BaseModel):
    """Schema for creating a ticket."""
    session_id: str
    subject: str
    description: str
    tier: Tier
    severity: Severity
    user_role: UserRole
    context: Dict[str, Any] = {}
    ai_analysis: Dict[str, Any] = {}


class TicketResponse(BaseModel):
    """Schema for ticket response."""
    id: str
    session_id: str
    subject: str
    description: str
    tier: Tier
    severity: Severity
    status: TicketStatus
    user_role: UserRole
    context: Dict[str, Any]
    ai_analysis: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TicketUpdate(BaseModel):
    """Schema for updating a ticket."""
    status: Optional[TicketStatus] = None
    tier: Optional[Tier] = None
    severity: Optional[Severity] = None


# Metrics API Schemas
class MetricsSummary(BaseModel):
    """Summary metrics response."""
    total_conversations: int
    total_tickets: int
    deflection_rate: float
    avg_confidence: float
    guardrail_activations: int
    tickets_by_tier: Dict[str, int]
    tickets_by_severity: Dict[str, int]


class TrendDataPoint(BaseModel):
    """Single data point in trend data."""
    timestamp: datetime
    value: float


class MetricsTrends(BaseModel):
    """Trend metrics response."""
    conversation_volume: List[TrendDataPoint]
    ticket_volume: List[TrendDataPoint]
    deflection_rate: List[TrendDataPoint]
    avg_confidence: List[TrendDataPoint]
