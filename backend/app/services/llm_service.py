"""LLM service abstraction layer for multiple providers."""
from typing import List, Dict, Any
from abc import ABC, abstractmethod
from app.utils.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        kb_context: str,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Generate a response from the LLM."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""
    
    def __init__(self):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.llm_model
    
    async def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        kb_context: str,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Generate response using OpenAI API."""
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add KB context and current message
        user_prompt = f"""Knowledge Base Context:
{kb_context}

User Question: {user_message}

Instructions: Answer the user's question using ONLY the information provided in the Knowledge Base Context above. If the information is not in the context, explicitly state "This information is not covered in the knowledge base." Do not make up information or use external knowledge."""
        
        messages.append({"role": "user", "content": user_prompt})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Low temperature for consistency
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            logger.info("llm_response_generated",
                       model=self.model,
                       tokens=response.usage.total_tokens)
            
            return answer
            
        except Exception as e:
            logger.error("llm_generation_failed", error=str(e))
            raise


class AnthropicProvider(LLMProvider):
    """Anthropic Claude LLM provider."""
    
    def __init__(self):
        from anthropic import AsyncAnthropic
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.llm_model
    
    async def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        kb_context: str,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Generate response using Anthropic API."""
        # Convert conversation history to Anthropic format
        messages = []
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add KB context and current message
        user_prompt = f"""Knowledge Base Context:
{kb_context}

User Question: {user_message}

Instructions: Answer the user's question using ONLY the information provided in the Knowledge Base Context above. If the information is not in the context, explicitly state "This information is not covered in the knowledge base." Do not make up information or use external knowledge."""
        
        messages.append({"role": "user", "content": user_prompt})
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.3,
                system=system_prompt,
                messages=messages
            )
            
            answer = response.content[0].text
            logger.info("llm_response_generated",
                       model=self.model,
                       tokens=response.usage.input_tokens + response.usage.output_tokens)
            
            return answer
            
        except Exception as e:
            logger.error("llm_generation_failed", error=str(e))
            raise


class LLMService:
    """Service for LLM operations with provider abstraction."""
    
    def __init__(self):
        """Initialize LLM service with configured provider."""
        if settings.llm_provider == "openai":
            self.provider = OpenAIProvider()
        elif settings.llm_provider == "anthropic":
            self.provider = AnthropicProvider()
        else:
            raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
        
        logger.info("llm_service_initialized", provider=settings.llm_provider)
    
    async def generate_grounded_response(
        self,
        user_message: str,
        kb_context: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Generate a grounded response based on KB context.
        
        Args:
            user_message: User's question
            kb_context: Retrieved knowledge base context
            conversation_history: Previous conversation turns
            
        Returns:
            Generated response
        """
        if conversation_history is None:
            conversation_history = []
        
        system_prompt = """You are an AI Help Desk Assistant for a cyber training platform. Your role is to:

1. Answer questions using ONLY the provided Knowledge Base context
2. Never fabricate information or use external knowledge
3. If information is not in the KB, explicitly say so
4. Provide clear, step-by-step guidance when available
5. Always cite KB article IDs when referencing procedures
6. Ask clarifying questions when context is ambiguous
7. Be helpful but stay within the bounds of the KB

Remember: You must NEVER provide information that is not explicitly in the Knowledge Base context."""
        
        response = await self.provider.generate_response(
            system_prompt=system_prompt,
            user_message=user_message,
            kb_context=kb_context,
            conversation_history=conversation_history
        )
        
        return response
