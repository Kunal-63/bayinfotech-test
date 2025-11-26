# Quick Start Guide

## Prerequisites
- Python 3.11+
- Supabase account (free tier)
- OpenAI API key or Anthropic API key

## Setup Steps

### 1. Create Supabase Project
1. Go to [supabase.com](https://supabase.com) and create a new project
2. Enable pgvector extension in SQL Editor:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Copy your database connection string from Settings → Database

### 2. Configure Environment
```bash
cd backend
cp .env.example .env
# Edit .env with your Supabase DATABASE_URL and API keys
```

### 3. Run Setup Script

**Windows:**
```bash
setup.bat
```

**Mac/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Create virtual environment
- Install dependencies
- Create database tables
- Ingest KB documents with embeddings

### 4. Start Server
```bash
# Make sure virtual environment is activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Test API
Open http://localhost:8000/docs for interactive API documentation

## Manual Setup (if scripts fail)

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install python-frontmatter

# Create tables
python init_db.py --create

# Verify setup
python init_db.py --verify

# Ingest KB
python -m app.kb.ingestion --ingest

# Start server
uvicorn app.main:app --reload
```

## Troubleshooting

**"No module named 'app'"**
- Make sure you're in the `backend` directory
- Ensure virtual environment is activated

**"Connection refused"**
- Check DATABASE_URL in .env
- Verify Supabase project is running
- Check password doesn't have special characters (URL encode if needed)

**"Extension 'vector' does not exist"**
- Enable pgvector in Supabase SQL Editor (see step 1.2)

## Next Steps
After successful setup:
1. Test chat endpoint with sample requests
2. Write workflow tests
3. Integrate with frontend
4. Deploy to Cloud Run/Render
