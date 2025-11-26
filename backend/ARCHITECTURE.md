# Backend Architecture

## Overview

The AI Help Desk backend is a FastAPI-based REST API that provides intelligent support ticket routing, knowledge base grounding, and guardrail enforcement for a cybersecurity training platform.

## Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: SQLite (embedded, deployed with code)
- **Vector Search**: In-memory cosine similarity (NumPy)
- **LLM Provider**: OpenAI (GPT-4 Turbo)
- **Embeddings**: OpenAI text-embedding-3-small (1536 dimensions)
- **Deployment**: Render (Web Service)

## Architecture Diagram

```
┌─────────────────┐
│   Frontend      │
│   (Vercel)      │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────────────────────────────┐
│         FastAPI Backend (Render)        │
│  ┌───────────────────────────────────┐  │
│  │      API Layer (app/api/)         │  │
│  │  - chat.py                        │  │
│  │  - tickets.py                     │  │
│  │  - metrics.py                     │  │
│  └──────────┬────────────────────────┘  │
│             │                            │
│  ┌──────────▼────────────────────────┐  │
│  │   Service Layer (app/services/)   │  │
│  │  - rag_service.py                 │  │
│  │  - tier_service.py                │  │
│  │  - guardrail_service.py           │  │
│  │  - llm_service.py                 │  │
│  │  - embedding_service.py           │  │
│  └──────────┬────────────────────────┘  │
│             │                            │
│  ┌──────────▼────────────────────────┐  │
│  │   Data Layer (app/models/)        │  │
│  │  - database.py (SQLAlchemy ORM)   │  │
│  │  - schemas.py (Pydantic)          │  │
│  └──────────┬────────────────────────┘  │
│             │                            │
│  ┌──────────▼────────────────────────┐  │
│  │      SQLite Database              │  │
│  │  - app.db (embedded file)         │  │
│  │  - 11 KB documents with           │  │
│  │    embeddings                     │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│   OpenAI API    │
│  - GPT-4 Turbo  │
│  - Embeddings   │
└─────────────────┘
```

## Core Components

### 1. RAG Pipeline (`rag_service.py`)

**Purpose**: Retrieve relevant knowledge base documents and generate grounded responses.

**Flow**:
1. Generate embedding for user query (OpenAI)
2. Fetch all KB documents from SQLite
3. Calculate cosine similarity in-memory (NumPy)
4. Sort and select top-k documents
5. Build context from retrieved documents
6. Generate response using LLM with KB context
7. Extract references and calculate confidence

**Key Features**:
- In-memory vector search (efficient for <1000 docs)
- Confidence scoring based on similarity scores
- KB reference extraction for citations

### 2. Tier Classification (`tier_service.py`)

**Purpose**: Route support requests to appropriate tier based on complexity and severity.

**Tiers**:
- **TIER_0**: Self-service (password reset, documentation)
- **TIER_1**: Basic troubleshooting (login issues, access problems)
- **TIER_2**: Technical support (environment config, container issues)
- **TIER_3**: Engineering escalation (VM crashes, data loss)
- **TIER_4**: Platform bugs (vendor issues, system-wide problems)

**Severity Levels**:
- **LOW**: Informational, no impact
- **MEDIUM**: Moderate impact, workaround available
- **HIGH**: Significant impact, blocks work
- **CRITICAL**: Data loss, system down

**Classification Logic**:
- Keyword-based tier matching
- Severity-based escalation
- Repeated failure detection
- KB coverage consideration

### 3. Guardrail System (`guardrail_service.py`)

**Purpose**: Prevent unauthorized actions and security violations.

**Guardrail Types**:
- **UNAUTHORIZED_ACCESS**: Attempts to access restricted resources
- **DISABLE_LOGGING**: Attempts to disable security logging
- **POLICY_VIOLATION**: Requests violating platform policies

**Enforcement**:
- Pattern matching on user messages
- Automatic escalation to TIER_3
- Safe response generation
- Event logging for audit

### 4. LLM Service (`llm_service.py`)

**Purpose**: Generate grounded responses using OpenAI GPT-4.

**Features**:
- System prompt with role definition
- KB context injection
- Conversation history support
- Streaming support (future)

### 5. Embedding Service (`embedding_service.py`)

**Purpose**: Generate vector embeddings for semantic search.

**Configuration**:
- Model: `text-embedding-3-small`
- Dimensions: 1536
- Batch processing support

## Data Models

### Database Schema

```sql
-- Conversations
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    session_id TEXT UNIQUE NOT NULL,
    user_role TEXT NOT NULL,
    context JSON,
    created_at DATETIME
);

-- Messages
CREATE TABLE messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    kb_references JSON,
    confidence REAL,
    tier TEXT,
    severity TEXT,
    created_at DATETIME,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

-- KB Documents
CREATE TABLE kb_documents (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding JSON,  -- 1536-dim vector as JSON array
    doc_metadata JSON,
    created_at DATETIME
);

-- Tickets
CREATE TABLE tickets (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    subject TEXT NOT NULL,
    description TEXT NOT NULL,
    tier TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT NOT NULL,
    user_role TEXT NOT NULL,
    context JSON,
    ai_analysis JSON,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (session_id) REFERENCES conversations(session_id)
);

-- Guardrail Events
CREATE TABLE guardrail_events (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    trigger_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    user_message TEXT NOT NULL,
    created_at DATETIME
);
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=sqlite:///./app.db

# LLM
OPENAI_API_KEY=sk-...
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
EMBEDDING_MODEL=text-embedding-3-small

# Application
LOG_LEVEL=INFO
ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=8000

# CORS
CORS_ORIGINS=http://localhost:5173,https://bayinfotech-test.onrender.com/
```

## Security Considerations

1. **API Key Management**: OpenAI keys stored in environment variables
2. **CORS**: Restricted to known frontend origins
3. **Guardrails**: Pattern-based request filtering
4. **Input Validation**: Pydantic schema validation
5. **Rate Limiting**: Handled by Render platform
6. **Logging**: Structured JSON logging for audit trails

## Performance Characteristics

- **Vector Search**: O(n) for n documents (~11 docs, <10ms)
- **LLM Response**: 2-5 seconds (OpenAI API latency)
- **Database Queries**: <5ms (SQLite, local file)
- **Embedding Generation**: ~100ms per query
