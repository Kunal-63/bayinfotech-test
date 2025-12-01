"""Response validation service for post-generation policy enforcement."""
from typing import Tuple, Optional, List
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ResponseValidator:
    """Service for validating LLM responses for policy compliance."""
    
    # Patterns that indicate policy violations in responses
    UNAUTHORIZED_INFO_PATTERNS = [
        "host machine", "hypervisor access", "root password", "admin credentials",
        "bypass security", "disable firewall", "escalate privileges",
        "sudo su", "ssh to host", "kernel modification"
    ]
    
    INSTRUCTION_DISCLOSURE_PATTERNS = [
        "my instructions", "i was told", "i am programmed to", "my system prompt",
        "according to my instructions", "i'm designed to", "my role is to"
    ]
    
    ROLE_CONFUSION_PATTERNS = [
        "as a system administrator", "as root", "as an attacker",
        "pretending to be", "acting as", "simulating a"
    ]
    
    HALLUCINATION_INDICATORS = [
        "i believe", "i think", "probably", "might be", "could be",
        "in my experience", "generally speaking", "typically"
    ]
    
    # Patterns that indicate proper KB grounding
    KB_GROUNDING_INDICATORS = [
        "according to", "kb-", "knowledge base", "documented in",
        "the procedure states", "as outlined in", "per the documentation"
    ]
    
    def validate_response(
        self,
        response: str,
        user_message: str,
        kb_references: List[dict],
        confidence: float
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate LLM response for policy compliance and quality.
        
        Args:
            response: Generated response from LLM
            user_message: Original user message
            kb_references: KB documents used for generation
            confidence: Confidence score from RAG
            
        Returns:
            Tuple of (is_valid, violation_type, safe_replacement)
        """
        response_lower = response.lower()
        
        # Check 1: Unauthorized information disclosure
        for pattern in self.UNAUTHORIZED_INFO_PATTERNS:
            if pattern in response_lower:
                logger.warning("response_validation_failed",
                             violation="unauthorized_info",
                             pattern=pattern)
                return (
                    False,
                    "UNAUTHORIZED_INFO",
                    "I cannot provide information about unauthorized system access. Please contact your administrator for assistance with privileged operations."
                )
        
        # Check 2: Instruction or prompt disclosure
        for pattern in self.INSTRUCTION_DISCLOSURE_PATTERNS:
            if pattern in response_lower:
                logger.warning("response_validation_failed",
                             violation="instruction_disclosure",
                             pattern=pattern)
                return (
                    False,
                    "INSTRUCTION_DISCLOSURE",
                    "I'm here to help with technical support questions. How can I assist you with your issue?"
                )
        
        # Check 3: Role confusion
        for pattern in self.ROLE_CONFUSION_PATTERNS:
            if pattern in response_lower:
                logger.warning("response_validation_failed",
                             violation="role_confusion",
                             pattern=pattern)
                return (
                    False,
                    "ROLE_CONFUSION",
                    "I'm an AI help desk assistant. I can only provide guidance based on our knowledge base. For privileged operations, please contact your system administrator."
                )
        
        # Check 4: Hallucination detection (if confidence is low)
        if confidence < 0.5:
            has_grounding = any(
                indicator in response_lower 
                for indicator in self.KB_GROUNDING_INDICATORS
            )
            has_hallucination_indicators = any(
                indicator in response_lower 
                for indicator in self.HALLUCINATION_INDICATORS
            )
            
            if has_hallucination_indicators and not has_grounding:
                logger.warning("response_validation_failed",
                             violation="potential_hallucination",
                             confidence=confidence)
                return (
                    False,
                    "HALLUCINATION",
                    "I don't have enough information in the knowledge base to answer this question accurately. Let me escalate this to a specialist who can help you."
                )
        
        # Check 5: Verify KB grounding for high-stakes queries
        if self._is_high_stakes_query(user_message):
            if not kb_references or confidence < 0.6:
                logger.warning("response_validation_failed",
                             violation="insufficient_grounding",
                             confidence=confidence)
                return (
                    False,
                    "INSUFFICIENT_GROUNDING",
                    "This is a critical operation that requires verified procedures. I'm escalating this to a specialist to ensure you get accurate guidance."
                )
        
        # Check 6: Response length sanity check
        if len(response) < 10:
            logger.warning("response_validation_failed",
                         violation="response_too_short")
            return (
                False,
                "INVALID_RESPONSE",
                "I encountered an issue generating a proper response. Please rephrase your question or contact support."
            )
        
        # All checks passed
        logger.info("response_validation_passed", confidence=confidence)
        return (True, None, None)
    
    def _is_high_stakes_query(self, message: str) -> bool:
        """Check if query involves high-stakes operations."""
        high_stakes_keywords = [
            "delete", "remove", "reset", "wipe", "format",
            "production", "critical", "emergency", "urgent",
            "password", "credentials", "access", "permissions",
            "firewall", "security", "kernel", "system"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in high_stakes_keywords)
    
    def sanitize_response(self, response: str) -> str:
        """
        Sanitize response to remove any potentially sensitive information.
        
        Args:
            response: Response to sanitize
            
        Returns:
            Sanitized response
        """
        # Remove any IP addresses
        import re
        sanitized = re.sub(
            r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            '[IP_ADDRESS]',
            response
        )
        
        # Remove any potential passwords or tokens
        sanitized = re.sub(
            r'(?:password|token|key|secret)[\s:=]+[\w\-]+',
            '[REDACTED]',
            sanitized,
            flags=re.IGNORECASE
        )
        
        return sanitized
