"""Enums for tier, severity, and user roles."""
from enum import Enum


class UserRole(str, Enum):
    """User role types."""
    TRAINEE = "trainee"
    OPERATOR = "operator"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"
    SUPPORT_ENGINEER = "support_engineer"


class Tier(str, Enum):
    """Support tier levels."""
    TIER_0 = "TIER_0"  # Self-service
    TIER_1 = "TIER_1"  # Basic support
    TIER_2 = "TIER_2"  # Advanced support
    TIER_3 = "TIER_3"  # Specialist
    TIER_4 = "TIER_4"  # Vendor escalation


class Severity(str, Enum):
    """Issue severity levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TicketStatus(str, Enum):
    """Ticket status types."""
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    ESCALATED = "ESCALATED"


class GuardrailTriggerType(str, Enum):
    """Types of guardrail triggers."""
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    DESTRUCTIVE_ACTION = "DESTRUCTIVE_ACTION"
    LOGGING_DISABLE = "LOGGING_DISABLE"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    ADVERSARIAL_PROMPT = "ADVERSARIAL_PROMPT"
    ESCALATION_OVERRIDE = "ESCALATION_OVERRIDE"
