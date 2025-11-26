"""Embedding service for generating and managing embeddings."""
from typing import List
import numpy as np
from app.utils.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self):
        """Initialize embedding service with configured model."""
        if settings.llm_provider == "openai":
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
            self.model = settings.embedding_model
            self.provider = "openai"
        else:
            # Fallback to sentence-transformers for local embeddings
            from sentence_transformers import SentenceTransformer
            self.model_name = "all-MiniLM-L6-v2"
            self.model = SentenceTransformer(self.model_name)
            self.provider = "sentence-transformers"
        
        logger.info("embedding_service_initialized",
                   provider=self.provider,
                   model=self.model if self.provider == "openai" else self.model_name)
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        if self.provider == "openai":
            return await self._generate_openai_embedding(text)
        else:
            return self._generate_local_embedding(text)
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if self.provider == "openai":
            return await self._generate_openai_embeddings(texts)
        else:
            return self._generate_local_embeddings(texts)
    
    async def _generate_openai_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI API."""
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text
            )
            embedding = response.data[0].embedding
            logger.debug("embedding_generated", provider="openai", dimension=len(embedding))
            return embedding
        except Exception as e:
            logger.error("embedding_generation_failed", provider="openai", error=str(e))
            raise
    
    async def _generate_openai_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts using OpenAI API."""
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            embeddings = [item.embedding for item in response.data]
            logger.debug("embeddings_generated",
                        provider="openai",
                        count=len(embeddings),
                        dimension=len(embeddings[0]))
            return embeddings
        except Exception as e:
            logger.error("embeddings_generation_failed", provider="openai", error=str(e))
            raise
    
    def _generate_local_embedding(self, text: str) -> List[float]:
        """Generate embedding using local sentence-transformers model."""
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            logger.debug("embedding_generated",
                        provider="sentence-transformers",
                        dimension=len(embedding))
            return embedding.tolist()
        except Exception as e:
            logger.error("embedding_generation_failed",
                        provider="sentence-transformers",
                        error=str(e))
            raise
    
    def _generate_local_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts using local model."""
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            logger.debug("embeddings_generated",
                        provider="sentence-transformers",
                        count=len(embeddings),
                        dimension=len(embeddings[0]))
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error("embeddings_generation_failed",
                        provider="sentence-transformers",
                        error=str(e))
            raise
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        
        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
