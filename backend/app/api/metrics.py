"""Metrics and analytics API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Dict, List

from app.models.schemas import MetricsSummary, MetricsTrends, TrendDataPoint
from app.models.database import Conversation, Message, Ticket, GuardrailEvent
from app.utils.db import get_db
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/summary", response_model=MetricsSummary)
async def get_metrics_summary(db: Session = Depends(get_db)):
    """Get overall metrics summary."""
    try:
        # Total conversations
        total_conversations = db.query(Conversation).count()
        
        # Total tickets
        total_tickets = db.query(Ticket).count()
        
        # Deflection rate (conversations that didn't create tickets)
        if total_conversations > 0:
            deflection_rate = ((total_conversations - total_tickets) / total_conversations) * 100
        else:
            deflection_rate = 0.0
        
        # Average confidence
        avg_confidence_result = db.query(func.avg(Message.confidence)).filter(
            Message.role == "assistant",
            Message.confidence.isnot(None)
        ).scalar()
        avg_confidence = float(avg_confidence_result) if avg_confidence_result else 0.0
        
        # Guardrail activations
        guardrail_activations = db.query(GuardrailEvent).count()
        
        # Tickets by tier
        tickets_by_tier = {}
        tier_counts = db.query(
            Ticket.tier,
            func.count(Ticket.id)
        ).group_by(Ticket.tier).all()
        
        for tier, count in tier_counts:
            tickets_by_tier[tier] = count
        
        # Tickets by severity
        tickets_by_severity = {}
        severity_counts = db.query(
            Ticket.severity,
            func.count(Ticket.id)
        ).group_by(Ticket.severity).all()
        
        for severity, count in severity_counts:
            tickets_by_severity[severity] = count
        
        logger.info("metrics_summary_generated",
                   total_conversations=total_conversations,
                   total_tickets=total_tickets,
                   deflection_rate=deflection_rate)
        
        return MetricsSummary(
            total_conversations=total_conversations,
            total_tickets=total_tickets,
            deflection_rate=round(deflection_rate, 2),
            avg_confidence=round(avg_confidence, 2),
            guardrail_activations=guardrail_activations,
            tickets_by_tier=tickets_by_tier,
            tickets_by_severity=tickets_by_severity
        )
        
    except Exception as e:
        logger.error("metrics_summary_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate metrics summary")


@router.get("/trends", response_model=MetricsTrends)
async def get_metrics_trends(days: int = 30, db: Session = Depends(get_db)):
    """Get trend metrics over time."""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Conversation volume by day
        conversation_volume = _get_daily_counts(
            db, Conversation, start_date, end_date
        )
        
        # Ticket volume by day
        ticket_volume = _get_daily_counts(
            db, Ticket, start_date, end_date
        )
        
        # Deflection rate by day
        deflection_rate = _calculate_daily_deflection(
            db, start_date, end_date
        )
        
        # Average confidence by day
        avg_confidence = _get_daily_avg_confidence(
            db, start_date, end_date
        )
        
        logger.info("metrics_trends_generated", days=days)
        
        return MetricsTrends(
            conversation_volume=conversation_volume,
            ticket_volume=ticket_volume,
            deflection_rate=deflection_rate,
            avg_confidence=avg_confidence
        )
        
    except Exception as e:
        logger.error("metrics_trends_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate metrics trends")


@router.get("/deflection")
async def get_deflection_metrics(db: Session = Depends(get_db)):
    """Get detailed deflection rate metrics."""
    try:
        total_conversations = db.query(Conversation).count()
        total_tickets = db.query(Ticket).count()
        
        if total_conversations > 0:
            deflection_rate = ((total_conversations - total_tickets) / total_conversations) * 100
        else:
            deflection_rate = 0.0
        
        # Issues resolved without tickets
        resolved_without_ticket = total_conversations - total_tickets
        
        logger.info("deflection_metrics_generated",
                   deflection_rate=deflection_rate,
                   resolved_without_ticket=resolved_without_ticket)
        
        return {
            "deflection_rate": round(deflection_rate, 2),
            "total_conversations": total_conversations,
            "total_tickets": total_tickets,
            "resolved_without_ticket": resolved_without_ticket
        }
        
    except Exception as e:
        logger.error("deflection_metrics_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate deflection metrics")


@router.get("/guardrails")
async def get_guardrail_metrics(db: Session = Depends(get_db)):
    """Get guardrail activation metrics."""
    try:
        total_activations = db.query(GuardrailEvent).count()
        
        # Activations by trigger type
        by_trigger_type = {}
        trigger_counts = db.query(
            GuardrailEvent.trigger_type,
            func.count(GuardrailEvent.id)
        ).group_by(GuardrailEvent.trigger_type).all()
        
        for trigger_type, count in trigger_counts:
            by_trigger_type[trigger_type] = count
        
        # Activations by severity
        by_severity = {}
        severity_counts = db.query(
            GuardrailEvent.severity,
            func.count(GuardrailEvent.id)
        ).group_by(GuardrailEvent.severity).all()
        
        for severity, count in severity_counts:
            by_severity[severity] = count
        
        logger.info("guardrail_metrics_generated",
                   total_activations=total_activations)
        
        return {
            "total_activations": total_activations,
            "by_trigger_type": by_trigger_type,
            "by_severity": by_severity
        }
        
    except Exception as e:
        logger.error("guardrail_metrics_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate guardrail metrics")


def _get_daily_counts(db: Session, model, start_date: datetime, end_date: datetime) -> List[TrendDataPoint]:
    """Get daily counts for a model."""
    counts = db.query(
        func.date(model.created_at).label('date'),
        func.count(model.id).label('count')
    ).filter(
        and_(
            model.created_at >= start_date,
            model.created_at <= end_date
        )
    ).group_by(func.date(model.created_at)).all()
    
    return [
        TrendDataPoint(timestamp=datetime.combine(date, datetime.min.time()), value=float(count))
        for date, count in counts
    ]


def _calculate_daily_deflection(db: Session, start_date: datetime, end_date: datetime) -> List[TrendDataPoint]:
    """Calculate daily deflection rate."""
    # This is a simplified version - in production, you'd want more sophisticated calculation
    daily_conversations = _get_daily_counts(db, Conversation, start_date, end_date)
    daily_tickets = _get_daily_counts(db, Ticket, start_date, end_date)
    
    # Create a map for easy lookup
    ticket_map = {dp.timestamp: dp.value for dp in daily_tickets}
    
    deflection_rates = []
    for conv_dp in daily_conversations:
        tickets = ticket_map.get(conv_dp.timestamp, 0)
        if conv_dp.value > 0:
            deflection = ((conv_dp.value - tickets) / conv_dp.value) * 100
        else:
            deflection = 0.0
        
        deflection_rates.append(
            TrendDataPoint(timestamp=conv_dp.timestamp, value=round(deflection, 2))
        )
    
    return deflection_rates


def _get_daily_avg_confidence(db: Session, start_date: datetime, end_date: datetime) -> List[TrendDataPoint]:
    """Get daily average confidence scores."""
    avg_scores = db.query(
        func.date(Message.created_at).label('date'),
        func.avg(Message.confidence).label('avg_confidence')
    ).filter(
        and_(
            Message.created_at >= start_date,
            Message.created_at <= end_date,
            Message.role == "assistant",
            Message.confidence.isnot(None)
        )
    ).group_by(func.date(Message.created_at)).all()
    
    return [
        TrendDataPoint(timestamp=datetime.combine(date, datetime.min.time()), value=round(float(avg), 2))
        for date, avg in avg_scores
    ]
