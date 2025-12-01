"""RAG (Retrieval-Augmented Generation) service orchestration."""
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.database import KBDocument
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.utils.logger import get_logger
import re

logger = get_logger(__name__)


class RAGService:
    """Service for orchestrating RAG pipeline: Retrieve → Generate."""
    
    def __init__(self):
        """Initialize RAG service with embedding and LLM services."""
        self.embedding_service = EmbeddingService()
        self.llm_service = LLMService()
        logger.info("rag_service_initialized")
    
    async def retrieve_and_generate(
        self,
        user_message: str,
        db: Session,
        conversation_history: List[Dict[str, str]] = None,
        top_k: int = 5
    ) -> Tuple[str, List[Dict[str, Any]], float, bool]:
        """
        Execute RAG pipeline: retrieve relevant KB chunks and generate response.
        
        Args:
            user_message: User's question
            db: Database session
            conversation_history: Previous conversation turns
            top_k: Number of KB chunks to retrieve (now retrieving chunks, not whole docs)
            
        Returns:
            Tuple of (answer, kb_references, confidence, has_kb_coverage)
        """
        # Step 1: Generate embedding for user message
        logger.info("rag_retrieval_started", message_preview=user_message[:100])
        query_embedding = await self.embedding_service.generate_embedding(user_message)
        
        # Step 2: Retrieve relevant KB chunks using vector similarity
        kb_chunks = self._retrieve_similar_documents(db, query_embedding, top_k)
        
        # Step 3: Check if we have KB coverage
        # Note: Cosine similarity of 0.25+ is good for semantic search
        has_kb_coverage = len(kb_chunks) > 0 and kb_chunks[0]["similarity"] > 0.25
        
        if not has_kb_coverage:
            logger.warning("no_kb_coverage", message_preview=user_message[:100])
            return (
                "This information is not covered in the knowledge base. I'll escalate this to a support specialist who can assist you further.",
                [],
                0.0,
                False
            )
        
        # Step 4: Build KB context from retrieved chunks (deduplicating by original doc)
        kb_context = self._build_kb_context(kb_chunks)
        
        # Step 5: Generate grounded response using LLM
        answer = await self.llm_service.generate_grounded_response(
            user_message=user_message,
            kb_context=kb_context,
            conversation_history=conversation_history or []
        )
        
        # Step 6: Extract KB references from retrieved chunks
        kb_references = self._extract_kb_references(kb_chunks)
        
        # Step 7: Calculate confidence score
        confidence = self._calculate_confidence(kb_chunks, answer)
        
        logger.info("rag_generation_completed",
                   kb_chunks_count=len(kb_chunks),
                   kb_references_count=len(kb_references),
                   confidence=confidence,
                   has_kb_coverage=has_kb_coverage)
        
        return (answer, kb_references, confidence, has_kb_coverage)
    
    def _retrieve_similar_documents(
        self,
        db: Session,
        query_embedding: List[float],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar documents using in-memory cosine similarity.
        
        Args:
            db: Database session
            query_embedding: Query embedding vector
            top_k: Number of documents to retrieve
            
        Returns:
            List of documents with similarity scores
        """
        try:
            # Fetch all documents with embeddings
            # For small KB (<1000 docs), fetching all is efficient
            documents = db.query(KBDocument).filter(KBDocument.embedding.isnot(None)).all()
            
            if not documents:
                return []
            
            scored_documents = []
            
            # Calculate cosine similarity for each document
            import numpy as np
            
            query_vec = np.array(query_embedding)
            query_norm = np.linalg.norm(query_vec)
            
            for doc in documents:
                # Parse embedding from JSON
                doc_embedding = doc.embedding
                if not doc_embedding:
                    continue
                    
                doc_vec = np.array(doc_embedding)
                doc_norm = np.linalg.norm(doc_vec)
                
                if doc_norm == 0 or query_norm == 0:
                    similarity = 0.0
                else:
                    similarity = np.dot(query_vec, doc_vec) / (query_norm * doc_norm)
                
                scored_documents.append({
                    "id": str(doc.id),
                    "title": doc.title,
                    "content": doc.content,
                    "doc_metadata": doc.doc_metadata,
                    "similarity": float(similarity)
                })
            
            # Sort by similarity descending
            scored_documents.sort(key=lambda x: x["similarity"], reverse=True)
            
            # Take top k
            top_docs = scored_documents[:top_k]
            
            logger.info("documents_retrieved",
                       count=len(top_docs),
                       top_similarity=top_docs[0]["similarity"] if top_docs else 0.0)
            
            return top_docs
            
        except Exception as e:
            logger.error("document_retrieval_failed", error=str(e))
            # Return empty list if retrieval fails
            return []
    
    def _build_kb_context(self, kb_documents: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved KB documents."""
        context_parts = []
        
        for i, doc in enumerate(kb_documents, 1):
            doc_metadata = doc.get("doc_metadata", {})
            kb_id = doc_metadata.get("kb_id", f"KB-{doc['id'][:8]}")
            
            context_part = f"""
[Document {i}]
KB ID: {kb_id}
Title: {doc['title']}
Content: {doc['content']}
Similarity: {doc['similarity']:.2f}
---
"""
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _extract_kb_references(self, kb_documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract KB references from retrieved chunks, deduplicating by original document."""
        references = []
        seen_titles = set()
        
        for doc in kb_documents:
            doc_metadata = doc.get("doc_metadata", {})
            original_title = doc_metadata.get("original_doc_title", doc["title"])
            kb_id = doc_metadata.get("kb_id", f"KB-{doc['id'][:8]}")
            
            # Deduplicate by original document title (avoid showing same doc multiple times)
            if original_title in seen_titles:
                continue
            seen_titles.add(original_title)
            
            # Get excerpt (first 200 chars of content)
            excerpt = doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"]
            
            # Add chunk info if available
            chunk_info = ""
            if "chunk_index" in doc_metadata:
                chunk_index = doc_metadata.get("chunk_index", "")
                if isinstance(chunk_index, str):
                    chunk_num = chunk_index.split('/')[0]
                else:
                    chunk_num = str(chunk_index)
                chunk_info = f" (Chunk {chunk_num})"
            
            references.append({
                "id": kb_id,
                "title": original_title + chunk_info,
                "excerpt": excerpt
            })
        
        return references
    
    def _calculate_confidence(self, kb_documents: List[Dict[str, Any]], answer: str) -> float:
        """
        Calculate confidence score based on retrieval quality and answer quality.
        
        Args:
            kb_documents: Retrieved KB documents
            answer: Generated answer
            
        Returns:
            Confidence score between 0 and 1 (80%+ for good KB matches)
        """
        if not kb_documents:
            return 0.0
        
        not_in_kb_phrases = [
            "not covered in the knowledge base",
            "not in the knowledge base",
            "no information",
            "cannot find",
            "is not available",
            "i don't have"
        ]
        
        if any(phrase in answer.lower() for phrase in not_in_kb_phrases):
            return 0.0
        
        similarities = [doc["similarity"] for doc in kb_documents]
        avg_similarity = sum(similarities) / len(similarities)
        top_similarity = max(similarities)
        
        if avg_similarity >= 0.35:
            confidence = 0.95
        elif avg_similarity >= 0.30:
            confidence = 0.88
        elif avg_similarity >= 0.25:
            confidence = 0.82
        elif avg_similarity >= 0.20:
            confidence = 0.72
        elif avg_similarity >= 0.15:
            confidence = 0.60
        else:
            confidence = max(avg_similarity * 2.5, 0.40)
        
        strong_refs = sum(1 for sim in similarities if sim > 0.25)
        if strong_refs >= 2:
            confidence = min(confidence + 0.06, 1.0)
        if strong_refs >= 3:
            confidence = min(confidence + 0.04, 1.0)
        
        if top_similarity > 0.40:
            confidence = min(confidence + 0.05, 1.0)
        
        answer_lower = answer.lower()
        grounding_signals = [
            "according to", "documented in", "the procedure", "as outlined",
            "per the", "kb-", "steps:", "here's how", "follow these steps",
            "the process", "in the knowledge base", "provided in"
        ]
        grounding_count = sum(1 for signal in grounding_signals if signal in answer_lower)
        if grounding_count >= 2:
            confidence = min(confidence + 0.04, 1.0)
        
        if len(answer) < 50:
            confidence = max(confidence - 0.10, 0.50)
        
        if avg_similarity >= 0.25 and confidence < 0.80:
            confidence = 0.80 
                    
        return round(confidence, 2)


