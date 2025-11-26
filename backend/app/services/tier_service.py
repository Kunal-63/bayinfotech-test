"""Tier classification service for routing support requests."""
from typing import Tuple
from app.models.enums import Tier, Severity, UserRole
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TierService:
    """Service for classifying support tier and severity."""
    
    # Keywords for tier classification
    TIER_0_KEYWORDS = [
        "password reset", "forgot password", "documentation", "how to",
        "where is", "find", "search", "lookup", "guide"
    ]
    
    TIER_1_KEYWORDS = [
        "lab access", "can't access", "login issue", "permission denied",
        "connection refused", "timeout", "slow", "not loading"
    ]
    
    TIER_2_KEYWORDS = [
        "authentication loop", "redirect", "keeps logging out",
        "environment wrong", "wrong toolset", "configuration",
        "container", "init failed", "startup failed"
    ]
    
    TIER_3_KEYWORDS = [
        "vm crash", "vm froze", "kernel panic", "data loss",
        "lost work", "system down", "critical error", "infrastructure"
    ]
    
    TIER_4_KEYWORDS = [
        "platform bug", "vendor", "missing feature", "broken feature",
        "system-wide", "affects everyone"
    ]
    
    # Keywords for severity classification
    CRITICAL_KEYWORDS = [
        "data loss", "lost work", "can't work", "blocked", "down",
        "crash", "kernel panic", "critical", "urgent", "emergency"
    ]
    
    HIGH_KEYWORDS = [
        "security breach", "breach", "unauthorized access", "hacked",
        "compromised", "vulnerability", "exploit"
    ]
    
    MEDIUM_KEYWORDS = [
        "slow", "timeout", "error", "issue", "problem", "not working",
        "configuration", "setup", "authentication", "can't login", 
        "access denied", "login loop", "redirect", "keeps logging out",
        "stuck", "frozen"
    ]
    
    def classify_tier_and_severity(
        self,
        message: str,
        user_role: UserRole,
        context: dict,
        kb_coverage: bool = True,
        repeated_failure: bool = False
    ) -> Tuple[Tier, Severity, bool]:
        """
        Classify tier and severity for a support request.
        
        Args:
            message: User message
            user_role: User's role
            context: Additional context (module, channel, etc.)
            kb_coverage: Whether KB has coverage for this issue
            repeated_failure: Whether this is a repeated failure
            
        Returns:
            Tuple of (tier, severity, needs_escalation)
        """
        message_lower = message.lower()
        
        # Determine severity first
        severity = self._classify_severity(message_lower)
        
        # Determine tier
        tier = self._classify_tier(message_lower, kb_coverage, repeated_failure, severity)
        
        # Determine if escalation is needed
        needs_escalation = self._needs_escalation(tier, severity, repeated_failure, kb_coverage)
        
        logger.info("tier_classification",
                   tier=tier.value,
                   severity=severity.value,
                   needs_escalation=needs_escalation,
                   user_role=user_role.value)
        
        return (tier, severity, needs_escalation)
    
    def _classify_severity(self, message_lower: str) -> Severity:
        """Classify severity based on message content."""
        if any(keyword in message_lower for keyword in self.CRITICAL_KEYWORDS):
            return Severity.CRITICAL
        elif any(keyword in message_lower for keyword in self.HIGH_KEYWORDS):
            return Severity.HIGH
        # Check for container/startup issues which block work (HIGH)
        elif any(keyword in message_lower for keyword in ["container", "startup failed", "init failed", "crash"]):
            return Severity.HIGH
        elif any(keyword in message_lower for keyword in self.MEDIUM_KEYWORDS):
            return Severity.MEDIUM
        else:
            return Severity.LOW
    
    def _classify_tier(
        self,
        message_lower: str,
        kb_coverage: bool,
        repeated_failure: bool,
        severity: Severity
    ) -> Tier:
        """Classify tier based on message content and context."""
        # Critical severity or repeated failures escalate to TIER_3
        if severity == Severity.CRITICAL or repeated_failure:
            return Tier.TIER_3
        
        # No KB coverage escalates to TIER_2 or TIER_3
        if not kb_coverage:
            if severity in [Severity.HIGH, Severity.CRITICAL]:
                return Tier.TIER_3
            else:
                return Tier.TIER_2
        
        # Check tier keywords
        if any(keyword in message_lower for keyword in self.TIER_4_KEYWORDS):
            return Tier.TIER_4
        elif any(keyword in message_lower for keyword in self.TIER_3_KEYWORDS):
            return Tier.TIER_3
        elif any(keyword in message_lower for keyword in self.TIER_2_KEYWORDS):
            return Tier.TIER_2
        elif any(keyword in message_lower for keyword in self.TIER_1_KEYWORDS):
            return Tier.TIER_1
        elif any(keyword in message_lower for keyword in self.TIER_0_KEYWORDS):
            return Tier.TIER_0
        else:
            # Default to TIER_1 for general queries
            return Tier.TIER_1
    
    def _needs_escalation(
        self,
        tier: Tier,
        severity: Severity,
        repeated_failure: bool,
        kb_coverage: bool
    ) -> bool:
        """Determine if escalation is needed."""
        # Always escalate TIER_3 and TIER_4
        if tier in [Tier.TIER_3, Tier.TIER_4]:
            return True
        
        # Escalate critical severity
        if severity == Severity.CRITICAL:
            return True
        
        # Escalate repeated failures
        if repeated_failure:
            return True
        
        # Escalate if no KB coverage and at least MEDIUM severity (blocks work)
        if not kb_coverage and severity in [Severity.HIGH, Severity.MEDIUM]:
            return True
            
        return False
