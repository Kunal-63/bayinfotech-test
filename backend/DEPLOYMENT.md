# Deployment Guide

## Platform: Render

The backend is deployed on [Render](https://render.com) as a Web Service.

**Live URL**: `https://bayinfotech-test.onrender.com`

---

## Prerequisites

1. Render account
2. GitHub repository connected to Render
3. OpenAI API key

---

## Initial Deployment

### 1. Create New Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **Web Service**
3. Connect your GitHub repository: `Kunal-63/bayinfotech-test`
4. Configure the service:
   - **Name**: `bayinfotech-test`
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 2. Environment Variables

Add the following environment variables in Render Dashboard:

```bash
# Database
DATABASE_URL=sqlite:///./app.db

# OpenAI
OPENAI_API_KEY=sk-your-api-key-here

# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536

# Application
LOG_LEVEL=INFO
ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=8000

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://bayinfotech-test-r9bncip32-kunal63s-projects.vercel.app

# Guardrails
GUARDRAIL_STRICT_MODE=true
MAX_CONVERSATION_HISTORY=10

# Analytics
ENABLE_METRICS=true
METRICS_RETENTION_DAYS=90
```

### 3. Deploy

Click **Create Web Service**. Render will:
1. Clone your repository
2. Install dependencies from `requirements.txt`
3. Start the FastAPI server
4. Assign a public URL

---

## Database Setup

### SQLite Embedded Database

The backend uses SQLite with the database file (`app.db`) committed to the repository.

**Why this works**:
- SQLite is file-based and deployed with the code
- No network calls needed
- Fast local queries
- Free (no external database costs)

**Initial Setup** (Local):

```bash
# Navigate to backend directory
cd backend

# Create database and ingest KB documents
python -m app.kb.ingestion --create-tables --ingest

# Commit the database file
git add app.db
git commit -m "Add populated SQLite database"
git push
```

**On Render**:
- The `app.db` file is deployed with your code
- Database is read-only in production (no writes from users)
- All KB documents are pre-loaded with embeddings

---

## Updating KB Documents

To add or update knowledge base documents:

1. **Edit KB files locally**:
   ```bash
   # Add/edit files in backend/app/kb/documents/
   vim backend/app/kb/documents/new-document.md
   ```

2. **Re-run ingestion**:
   ```bash
   cd backend
   python -m app.kb.ingestion --ingest
   ```

3. **Commit updated database**:
   ```bash
   git add app.db
   git commit -m "Update KB documents"
   git push
   ```

4. **Render auto-deploys** the updated database

---

## Deployment Workflow

### Automatic Deployments

Render automatically deploys when you push to the `main` branch:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

Render will:
1. Detect the push
2. Build the new version
3. Run health checks
4. Switch traffic to new version (zero-downtime)

### Manual Deployments

From Render Dashboard:
1. Go to your service
2. Click **Manual Deploy** → **Deploy latest commit**

---

## Monitoring

### Logs

View logs in Render Dashboard:
1. Go to your service
2. Click **Logs** tab
3. Filter by log level (INFO, WARNING, ERROR)

**Structured Logging**:
All logs are JSON-formatted for easy parsing:
```json
{
  "event": "chat_request_received",
  "session_id": "session-123",
  "user_role": "trainee",
  "timestamp": "2024-01-01T00:00:00Z"
}
```
