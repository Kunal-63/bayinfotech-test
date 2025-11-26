"""Guardrail service for content filtering and policy enforcement."""
from typing import Tuple, Optional
from app.models.enums import GuardrailTriggerType, Severity
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GuardrailService:
    """Service for enforcing guardrails and policy constraints."""
    
    # Patterns that trigger guardrails
    UNAUTHORIZED_ACCESS_PATTERNS = [
        "host machine", "hypervisor", "access host", "ssh to host",
        "root access", "sudo su", "escalate privileges", "admin access",
        "bypass security", "disable firewall"
    ]
    
    DESTRUCTIVE_ACTION_PATTERNS = [
        "reset all", "delete all", "remove all", "wipe", "format",
        "destroy", "terminate all", "kill all processes", "shutdown all",
        "reset environment", "factory reset"
    ]
    
    LOGGING_DISABLE_PATTERNS = [
        "disable logging", "turn off logging", "stop logging",
        "disable monitoring", "turn off monitoring", "hide logs",
        "delete logs", "clear logs", "bypass audit"
    ]
    
    KERNEL_DEBUG_PATTERNS = [
        "kernel debug", "kernel panic fix", "modify kernel",
        "kernel parameters", "sysctl", "/proc/sys", "kernel module"
    ]
    
    ESCALATION_OVERRIDE_PATTERNS = [
        "don't escalate", "do not escalate", "skip escalation",
        "bypass escalation", "ignore escalation", "no ticket"
    ]
    
    ADVERSARIAL_PATTERNS = [
        "ignore previous", "ignore instructions", "disregard",
        "act as", "pretend to be", "you are now", "new role",
        "jailbreak", "bypass rules", "override policy"
    ]
    
    DNS_EDITING_PATTERNS = [
        "edit /etc/hosts", "modify /etc/hosts", "change /etc/hosts",
        "edit hosts file", "modify hosts file"
    ]
    
    def check_guardrails(self, message: str) -> Tuple[bool, Optional[GuardrailTriggerType], Optional[Severity], Optional[str]]:
        """
        Check if message triggers any guardrails.
        
        Args:
            message: User message to check
            
        Returns:
            Tuple of (is_blocked, trigger_type, severity, reason)
        """
        message_lower = message.lower()
        
        # Check for unauthorized access attempts
        if any(pattern in message_lower for pattern in self.UNAUTHORIZED_ACCESS_PATTERNS):
            logger.warning("guardrail_triggered", 
                          trigger_type="UNAUTHORIZED_ACCESS",
                          message_preview=message[:100])
            return (
                True,
                GuardrailTriggerType.UNAUTHORIZED_ACCESS,
                Severity.HIGH,
                "This request involves unauthorized system access which is not permitted. Please contact your administrator if you need elevated privileges."
            )
        
        # Check for destructive actions
        if any(pattern in message_lower for pattern in self.DESTRUCTIVE_ACTION_PATTERNS):
            logger.warning("guardrail_triggered",
                          trigger_type="DESTRUCTIVE_ACTION",
                          message_preview=message[:100])
            return (
                True,
                GuardrailTriggerType.DESTRUCTIVE_ACTION,
                Severity.CRITICAL,
                "This request involves potentially destructive actions that require proper authorization. Please submit a formal request through your supervisor."
            )
        
        # Check for logging/monitoring disable attempts
        if any(pattern in message_lower for pattern in self.LOGGING_DISABLE_PATTERNS):
            logger.warning("guardrail_triggered",
                          trigger_type="LOGGING_DISABLE",
                          message_preview=message[:100])
            return (
                True,
                GuardrailTriggerType.LOGGING_DISABLE,
                Severity.CRITICAL,
                "Disabling logging or monitoring is a security violation and is not permitted. This incident has been logged."
            )
        
        # Check for escalation override attempts
        if any(pattern in message_lower for pattern in self.ESCALATION_OVERRIDE_PATTERNS):
            logger.warning("guardrail_triggered",
                          trigger_type="ESCALATION_OVERRIDE",
                          message_preview=message[:100])
            return (
                True,
                GuardrailTriggerType.ESCALATION_OVERRIDE,
                Severity.MEDIUM,
                "Escalation procedures are mandatory for certain issues and cannot be bypassed. The system will follow standard escalation protocols."
            )
        
        # Check for adversarial/jailbreak attempts
        if any(pattern in message_lower for pattern in self.ADVERSARIAL_PATTERNS):
            logger.warning("guardrail_triggered",
                          trigger_type="ADVERSARIAL_PROMPT",
                          message_preview=message[:100])
            return (
                True,
                GuardrailTriggerType.ADVERSARIAL_PROMPT,
                Severity.HIGH,
                "I'm designed to assist with legitimate help desk queries only. I cannot modify my behavior or bypass security policies."
            )
        
        # Check for unsafe DNS editing
        if any(pattern in message_lower for pattern in self.DNS_EDITING_PATTERNS):
            logger.info("guardrail_triggered",
                       trigger_type="POLICY_VIOLATION",
                       message_preview=message[:100])
            return (
                True,
                GuardrailTriggerType.POLICY_VIOLATION,
                Severity.MEDIUM,
                "Editing /etc/hosts directly is not recommended. Please use the proper DNS troubleshooting procedures from the knowledge base."
            )
        
        # No guardrail triggered
        return (False, None, None, None)
    
    def get_safe_response(self, trigger_type: GuardrailTriggerType, reason: str) -> str:
        """
        Generate a safe response for blocked requests.
        
        Args:
            trigger_type: Type of guardrail that was triggered
            reason: Reason for blocking
            
        Returns:
            Safe response message
        """
        return f"I cannot assist with this request. {reason}"
