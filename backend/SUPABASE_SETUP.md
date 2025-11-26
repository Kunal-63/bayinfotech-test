# Supabase Database Setup Guide

## Step 1: Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up or log in
3. Click "New Project"
4. Fill in:
   - **Project Name**: `ai-helpdesk` (or your choice)
   - **Database Password**: Choose a strong password (save this!)
   - **Region**: Choose closest to your users
   - **Pricing Plan**: Free tier is sufficient for development
5. Click "Create new project"
6. Wait 2-3 minutes for project to initialize

## Step 2: Enable pgvector Extension

1. In your Supabase project dashboard, go to **SQL Editor**
2. Click "New Query"
3. Run this SQL:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT * FROM pg_extension WHERE extname = 'vector';
```

4. Click "Run" - you should see the vector extension listed

## Step 3: Get Database Connection String

1. In Supabase dashboard, go to **Settings** → **Database**
2. Scroll to **Connection String** section
3. Select **URI** tab
4. Copy the connection string (looks like):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```
5. Replace `[YOUR-PASSWORD]` with your actual database password

## Step 4: Configure Backend Environment

1. In your backend folder, create `.env` file:

```bash
cd backend
cp .env.example .env
```

2. Edit `.env` and add your Supabase connection string:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres

# LLM Provider (choose one)
OPENAI_API_KEY=your-openai-api-key-here
# ANTHROPIC_API_KEY=your-anthropic-api-key-here

# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536

# Application Settings
LOG_LEVEL=INFO
ENVIRONMENT=development
API_HOST=0.0.0.0
API_PORT=8000

# CORS Settings (update with your frontend URL later)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Guardrail Settings
GUARDRAIL_STRICT_MODE=true
MAX_CONVERSATION_HISTORY=10

# Analytics
ENABLE_METRICS=true
METRICS_RETENTION_DAYS=90
```

## Step 5: Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install python-frontmatter  # For KB ingestion
```

## Step 6: Create Database Tables

```bash
# Create all tables
python -m app.kb.ingestion --create-tables
```

Expected output:
```
{"event": "creating_database_tables", "timestamp": "..."}
{"event": "database_tables_created", "timestamp": "..."}
```

## Step 7: Ingest Knowledge Base Documents

```bash
# Ingest all KB documents and generate embeddings
python -m app.kb.ingestion --ingest
```

This will:
- Read all 10 KB markdown files
- Parse frontmatter metadata
- Generate embeddings for each document
- Store in Supabase database

Expected output:
```
{"event": "kb_ingestion_started", "directory": "...", "timestamp": "..."}
{"event": "kb_files_found", "count": 10, "timestamp": "..."}
{"event": "generating_embedding", "kb_id": "kb-platform-overview", "timestamp": "..."}
{"event": "kb_document_ingested", "kb_id": "kb-platform-overview", "title": "...", "timestamp": "..."}
...
{"event": "kb_ingestion_completed", "total_documents": 10, "timestamp": "..."}
```

## Step 8: Verify Database Setup

1. Go back to Supabase dashboard
2. Navigate to **Table Editor**
3. You should see these tables:
   - `conversations`
   - `messages`
   - `kb_documents` (with 10 rows)
   - `tickets`
   - `guardrail_events`

4. Click on `kb_documents` table
5. Verify:
   - 10 rows present
   - `embedding` column has vector data
   - `metadata` column has JSON data

## Step 9: Test Backend Locally

```bash
# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

## Step 10: Test API Endpoints

Open your browser or use curl:

1. **Health Check**:
   ```
   http://localhost:8000/health
   ```
   Should return: `{"status": "healthy"}`

2. **API Documentation**:
   ```
   http://localhost:8000/docs
   ```
   Should show interactive API documentation

3. **Test Chat Endpoint** (using curl or Postman):
   ```bash
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{
       "session_id": "test-session-123",
       "message": "I keep getting redirected to the login page after I log in",
       "user_role": "trainee",
       "context": {
         "module": "lab-7",
         "channel": "self-service-portal"
       }
     }'
   ```

   Expected response:
   ```json
   {
     "answer": "Here are the steps to resolve the login redirection issue...",
     "kb_references": [
       {
         "id": "kb-access-authentication",
         "title": "Access and Authentication Troubleshooting",
         "excerpt": "..."
       }
     ],
     "confidence": 0.93,
     "tier": "TIER_1",
     "severity": "MEDIUM",
     "needs_escalation": false,
     "guardrail": {
       "blocked": false,
       "reason": null
     }
   }
   ```

## Troubleshooting

### Error: "No module named 'app'"
- Make sure you're in the `backend` directory
- Ensure virtual environment is activated

### Error: "Connection refused" to database
- Check your DATABASE_URL is correct
- Verify Supabase project is running
- Check if password has special characters (URL encode them)

### Error: "Extension 'vector' does not exist"
- Go back to Step 2 and enable pgvector extension in Supabase SQL Editor

### Error: "No such file or directory: '.env'"
- Create `.env` file from `.env.example`
- Make sure you're in the `backend` directory

### Embeddings generation is slow
- This is normal for first run (10 documents × ~30 seconds each)
- OpenAI API has rate limits
- Consider using sentence-transformers for faster local embeddings (no API calls)

## Next Steps

After successful setup:
1. ✅ Database is ready with pgvector
2. ✅ All KB documents ingested with embeddings
3. ✅ Backend API running locally
4. ⏭️ Write workflow tests
5. ⏭️ Integrate frontend
6. ⏭️ Deploy to Cloud Run/Render

## Supabase Dashboard Quick Links

- **Table Editor**: View and edit data
- **SQL Editor**: Run custom queries
- **Database**: Connection settings
- **API**: Auto-generated REST API (not used in this project)
- **Logs**: View database logs
