"""Test script to debug vector search."""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from app.utils.config import settings
from app.utils.db import SessionLocal
from app.services.embedding_service import EmbeddingService
from sqlalchemy import text


async def test_vector_search():
    """Test vector search with a sample query."""
    
    # Initialize embedding service
    embedding_service = EmbeddingService()
    
    # Test query
    test_message = "I keep getting redirected to the login page after I log in"
    
    print(f"Testing query: {test_message}")
    print("=" * 80)
    
    # Generate embedding
    print("\n1. Generating embedding...")
    embedding = await embedding_service.generate_embedding(test_message)
    print(f"   Embedding dimension: {len(embedding)}")
    print(f"   First 5 values: {embedding[:5]}")
    
    # Query database
    print("\n2. Querying database...")
    db = SessionLocal()
    
    try:
        # First, check how many documents we have
        count_query = text("SELECT COUNT(*) FROM kb_documents WHERE embedding IS NOT NULL")
        result = db.execute(count_query)
        count = result.scalar()
        print(f"   Total KB documents with embeddings: {count}")
        
        # Now do the vector search
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"
        
        query = text(f"""
            SELECT 
                id,
                title,
                1 - (embedding <=> '{embedding_str}'::vector) as similarity
            FROM kb_documents
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> '{embedding_str}'::vector
            LIMIT 5
        """)
        
        result = db.execute(query)
        
        print("\n3. Top 5 results:")
        print("-" * 80)
        for i, row in enumerate(result, 1):
            print(f"   {i}. {row.title}")
            print(f"      Similarity: {row.similarity:.4f}")
            print(f"      ID: {row.id}")
            print()
        
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_vector_search())
