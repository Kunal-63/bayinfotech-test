# AI Help Desk Backend

FastAPI backend for the BayInfotech AI Help Desk Platform with RAG (Retrieval-Augmented Generation) pipeline.

## Features

- ✅ **RAG Pipeline**: Semantic search with pgvector + OpenAI/Anthropic LLM
- ✅ **Guardrails**: 6 types of content filtering and policy enforcement
- ✅ **Tier Routing**: Deterministic classification (TIER_0 to TIER_4)
- ✅ **Severity Detection**: LOW/MEDIUM/HIGH/CRITICAL classification
- ✅ **Analytics**: Deflection rate, confidence scores, guardrail metrics
- ✅ **Conversation History**: Session-based context management
- ✅ **Structured Logging**: JSON logs with structlog

## Tech Stack

- **Framework**: FastAPI 0.109+
- **Database**: PostgreSQL with pgvector extension
- **LLM**: OpenAI GPT-4 or Anthropic Claude
- **Embeddings**: OpenAI text-embedding-3-small or Sentence Transformers
- **ORM**: SQLAlchemy 2.0
- **Testing**: Pytest

## Quick Start

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Up Database

```bash
# Install PostgreSQL with pgvector
# On Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib
sudo apt-get install postgresql-14-pgvector

# Create database
createdb ai_helpdesk

# Enable pgvector extension
psql ai_helpdesk -c "CREATE EXTENSION vector;"
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`: LLM provider key
- `LLM_PROVIDER`: `openai` or `anthropic`
- `LLM_MODEL`: Model name (e.g., `gpt-4-turbo-preview`)

### 4. Run Migrations

```bash
# Create tables
python -m app.kb.ingestion --create-tables

# Ingest KB documents
python -m app.kb.ingestion --ingest
```

### 5. Start Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: `http://localhost:8000`
API docs: `http://localhost:8000/docs`

## API Endpoints

### Chat
- `POST /api/chat` - Send message and get AI response

### Tickets
- `POST /api/tickets` - Create support ticket
- `GET /api/tickets` - List tickets (with filters)
- `GET /api/tickets/{id}` - Get ticket details
- `PATCH /api/tickets/{id}` - Update ticket

### Metrics
- `GET /api/metrics/summary` - Overall metrics
- `GET /api/metrics/trends` - Time-series data
- `GET /api/metrics/deflection` - Deflection rate
- `GET /api/metrics/guardrails` - Guardrail activations

## Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   ├── chat.py
│   │   ├── tickets.py
│   │   └── metrics.py
│   ├── services/         # Business logic
│   │   ├── rag_service.py
│   │   ├── llm_service.py
│   │   ├── embedding_service.py
│   │   ├── guardrail_service.py
│   │   └── tier_service.py
│   ├── models/           # Database & schemas
│   │   ├── database.py
│   │   ├── schemas.py
│   │   └── enums.py
│   ├── utils/            # Utilities
│   │   ├── config.py
│   │   ├── db.py
│   │   └── logger.py
│   ├── kb/               # Knowledge base
│   │   ├── documents/    # KB markdown files
│   │   └── ingestion.py  # KB ingestion script
│   └── main.py           # FastAPI app
├── tests/                # Tests
│   ├── unit/
│   ├── e2e/
│   └── workflows/
├── Dockerfile
├── requirements.txt
└── .env.example
```

## Knowledge Base

KB documents are stored in `app/kb/documents/` as Markdown files with YAML frontmatter:

```markdown
---
kb_id: KB-AUTH-001
title: Login Redirection Troubleshooting
tier: TIER_2
severity: MEDIUM
tags: [authentication, login]
---

# Content here...
```

Current KB documents (6/12 required):
1. `auth-loop-troubleshooting.md` - Authentication loop failure
2. `vm-crash-recovery.md` - Lab VM crash & data recovery
3. `unauthorized-access-policy.md` - Unauthorized access policy
4. `logging-policy.md` - Logging and monitoring policy
5. `dns-troubleshooting.md` - DNS resolution issues
6. `container-init-failure.md` - Container initialization failure

## Guardrails

The system enforces 6 types of guardrails:

1. **UNAUTHORIZED_ACCESS**: Host machine access, privilege escalation
2. **DESTRUCTIVE_ACTION**: Reset all, delete all, wipe commands
3. **LOGGING_DISABLE**: Disable logging/monitoring attempts
4. **POLICY_VIOLATION**: DNS /etc/hosts editing, etc.
5. **ADVERSARIAL_PROMPT**: Jailbreak attempts, role manipulation
6. **ESCALATION_OVERRIDE**: "Don't escalate" requests

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test category
pytest tests/unit/
pytest tests/e2e/
pytest tests/workflows/
```

## Docker Deployment

```bash
# Build image
docker build -t ai-helpdesk-backend .

# Run container
docker run -p 8000:8000 --env-file .env ai-helpdesk-backend
```