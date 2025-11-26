"""Database initialization script for Supabase."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.models.database import Base
from app.utils.db import engine
from app.utils.logger import setup_logging, get_logger
from sqlalchemy import text

setup_logging()
logger = get_logger(__name__)


def create_tables():
    """Create all database tables."""
    logger.info("creating_database_tables")
    
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("database_tables_created")
        
        # Verify pgvector extension
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM pg_extension WHERE extname = 'vector'"))
            if result.fetchone():
                logger.info("pgvector_extension_verified")
            else:
                logger.warning("pgvector_extension_not_found", 
                             message="Please enable pgvector extension in Supabase SQL Editor")
        
        return True
        
    except Exception as e:
        logger.error("database_table_creation_failed", error=str(e))
        return False


def verify_setup():
    """Verify database setup is correct."""
    logger.info("verifying_database_setup")
    
    try:
        with engine.connect() as conn:
            # Check if tables exist
            tables = ['conversations', 'messages', 'kb_documents', 'tickets', 'guardrail_events']
            
            for table in tables:
                result = conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = '{table}'
                    )
                """))
                exists = result.fetchone()[0]
                
                if exists:
                    logger.info("table_verified", table=table)
                else:
                    logger.error("table_missing", table=table)
                    return False
            
            # Check pgvector extension
            result = conn.execute(text("SELECT * FROM pg_extension WHERE extname = 'vector'"))
            if not result.fetchone():
                logger.error("pgvector_extension_missing")
                print("\n⚠️  pgvector extension is not enabled!")
                print("Please run this SQL in Supabase SQL Editor:")
                print("CREATE EXTENSION IF NOT EXISTS vector;")
                return False
            
            logger.info("database_setup_verified")
            return True
            
    except Exception as e:
        logger.error("database_verification_failed", error=str(e))
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Initialization')
    parser.add_argument('--create', action='store_true', help='Create database tables')
    parser.add_argument('--verify', action='store_true', help='Verify database setup')
    
    args = parser.parse_args()
    
    if args.create:
        success = create_tables()
        if success:
            print("\n✅ Database tables created successfully!")
            print("Next step: Run 'python -m app.kb.ingestion --ingest' to load KB documents")
        else:
            print("\n❌ Failed to create database tables. Check logs for details.")
            sys.exit(1)
    
    elif args.verify:
        success = verify_setup()
        if success:
            print("\n✅ Database setup verified successfully!")
        else:
            print("\n❌ Database setup verification failed. Check logs for details.")
            sys.exit(1)
    
    else:
        print("Usage: python init_db.py [--create] [--verify]")
        print("  --create: Create database tables")
        print("  --verify: Verify database setup")
