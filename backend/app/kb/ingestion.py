"""Knowledge base document ingestion script."""
import os
import sys
import asyncio
from pathlib import Path
from typing import List, Dict, Any
# import frontmatter  # Removed due to module conflict, using manual YAML parsing instead
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.models.database import Base, KBDocument
from app.services.embedding_service import EmbeddingService
from app.utils.config import settings
from app.utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


class KBIngestion:
    """Knowledge base document ingestion system."""
    
    def __init__(self):
        """Initialize ingestion system."""
        self.embedding_service = EmbeddingService()
        self.engine = create_engine(settings.database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.kb_dir = Path(__file__).parent / "documents"
    
    def create_tables(self):
        """Create database tables."""
        logger.info("creating_database_tables")
        Base.metadata.create_all(bind=self.engine)
        logger.info("database_tables_created")
    
    async def ingest_documents(self):
        """Ingest all KB documents from the documents directory."""
        logger.info("kb_ingestion_started", directory=str(self.kb_dir))
        
        if not self.kb_dir.exists():
            logger.error("kb_directory_not_found", directory=str(self.kb_dir))
            return
        
        # Get all markdown files
        md_files = list(self.kb_dir.glob("*.md"))
        logger.info("kb_files_found", count=len(md_files))
        
        db = self.SessionLocal()
        try:
            for md_file in md_files:
                await self._ingest_document(db, md_file)
            
            db.commit()
            logger.info("kb_ingestion_completed", total_documents=len(md_files))
            
        except Exception as e:
            logger.error("kb_ingestion_failed", error=str(e))
            db.rollback()
            raise
        finally:
            db.close()
    
    async def _ingest_document(self, db, file_path: Path):
        """Ingest a single KB document."""
        try:
            # Parse markdown with frontmatter manually
            import yaml
            
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            # Split frontmatter and content
            if file_content.startswith('---'):
                parts = file_content.split('---', 2)
                if len(parts) >= 3:
                    metadata_str = parts[1]
                    content = parts[2].strip()
                    doc_metadata = yaml.safe_load(metadata_str) or {}
                else:
                    doc_metadata = {}
                    content = file_content
            else:
                doc_metadata = {}
                content = file_content
            
            # Convert dates to strings for JSON serialization
            for key, value in list(doc_metadata.items()):
                if hasattr(value, 'isoformat'):  # datetime, date objects
                    doc_metadata[key] = value.isoformat()
            
            kb_id = doc_metadata.get('kb_id', file_path.stem)
            title = doc_metadata.get('title', file_path.stem)
            
            # Check if document already exists by title
            existing = db.query(KBDocument).filter(
                KBDocument.title == title
            ).first()
            
            if existing:
                logger.info("kb_document_exists_skipping", kb_id=kb_id)
                return
            
            # Generate embedding for content
            logger.info("generating_embedding", kb_id=kb_id)
            embedding = await self.embedding_service.generate_embedding(content)
            
            # Create KB document
            kb_doc = KBDocument(
                title=title,
                content=content,
                embedding=embedding,
                doc_metadata=doc_metadata
            )
            
            db.add(kb_doc)
            logger.info("kb_document_ingested", kb_id=kb_id, title=title)
            
        except Exception as e:
            logger.error("kb_document_ingestion_failed",
                        file=file_path.name,
                        error=str(e))
            raise
    
    async def reindex_all(self):
        """Reindex all existing KB documents (regenerate embeddings)."""
        logger.info("kb_reindexing_started")
        
        db = self.SessionLocal()
        try:
            documents = db.query(KBDocument).all()
            logger.info("kb_documents_to_reindex", count=len(documents))
            
            for doc in documents:
                logger.info("reindexing_document", kb_id=doc.doc_metadata.get('kb_id'))
                embedding = await self.embedding_service.generate_embedding(doc.content)
                doc.embedding = embedding
            
            db.commit()
            logger.info("kb_reindexing_completed", total_documents=len(documents))
            
        except Exception as e:
            logger.error("kb_reindexing_failed", error=str(e))
            db.rollback()
            raise
        finally:
            db.close()


async def main():
    """Main ingestion script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='KB Document Ingestion')
    parser.add_argument('--create-tables', action='store_true',
                       help='Create database tables')
    parser.add_argument('--ingest', action='store_true',
                       help='Ingest KB documents')
    parser.add_argument('--reindex', action='store_true',
                       help='Reindex all documents')
    
    args = parser.parse_args()
    
    ingestion = KBIngestion()
    
    if args.create_tables:
        ingestion.create_tables()
    
    if args.ingest:
        await ingestion.ingest_documents()
    
    if args.reindex:
        await ingestion.reindex_all()
    
    if not (args.create_tables or args.ingest or args.reindex):
        print("Usage: python -m app.kb.ingestion [--create-tables] [--ingest] [--reindex]")


if __name__ == "__main__":
    asyncio.run(main())
