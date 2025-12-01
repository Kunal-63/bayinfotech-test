"""Database models using SQLAlchemy."""
from sqlalchemy import Column, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.utils.db import Base
# Removed pgvector for SQLite compatibility


class Conversation(Base):
    """Conversation session model."""
    __tablename__ = "conversations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), unique=True, nullable=False, index=True)
    user_role = Column(String(50), nullable=False)
    context = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="conversation")


class Message(Base):
    """Chat message model."""
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    kb_references = Column(JSON, default=[])
    confidence = Column(Float, nullable=True)
    tier = Column(String(20), nullable=True)
    severity = Column(String(20), nullable=True)
    guardrail_blocked = Column(Boolean, default=False)
    guardrail_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class KBDocument(Base):
    """Knowledge base document/chunk model.
    
    Now supports both full documents and chunks. Each chunk stores:
    - content: chunk text
    - chunk_index: which chunk this is (0-based) or None for full doc
    - chunk_count: total chunks in document or None for full doc
    - original_doc_title: original document title (same for all chunks of same doc)
    """
    __tablename__ = "kb_documents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(JSON)  # Stored as JSON array for SQLite
    doc_metadata = Column(JSON, default={})  # version, timestamp, tags, tier, severity, chunk_index, chunk_count
    chunk_index = Column(String(10), nullable=True)  # e.g., "0/10" or None for full doc
    original_doc_id = Column(String(36), nullable=True)  # reference to parent doc if this is a chunk
    created_at = Column(DateTime, default=datetime.utcnow)


class Ticket(Base):
    """Support ticket model."""
    __tablename__ = "tickets"
    
    id = Column(String(50), primary_key=True)  # e.g., TICKET-001
    session_id = Column(String(36), ForeignKey("conversations.session_id"), nullable=False)
    subject = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    tier = Column(String(20), nullable=False)
    severity = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="OPEN")
    user_role = Column(String(50), nullable=False)
    context = Column(JSON, default={})
    ai_analysis = Column(JSON, default={})  # tags, sentiment, kb_recommendations
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="tickets")


class GuardrailEvent(Base):
    """Guardrail activation event model."""
    __tablename__ = "guardrail_events"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), nullable=False, index=True)
    message_id = Column(String(36), ForeignKey("messages.id"), nullable=True)
    trigger_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    user_message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
