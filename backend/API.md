# API Documentation

## Base URL

**Production**: `https://bayinfotech-test.onrender.com`  
**Local**: `http://localhost:8000`

## Authentication

Currently, no authentication is required. Future versions will implement JWT-based authentication.

## Endpoints

### Health Check

#### `GET /`

Root endpoint for health check.

**Response**:
```json
{
  "status": "healthy",
  "service": "AI Help Desk API",
  "version": "1.0.0"
}
```

#### `GET /health`

Health check endpoint.

**Response**:
```json
{
  "status": "healthy"
}
```

---

### Chat API

#### `POST /api/chat`

Send a message to the AI Help Desk and receive a grounded response.

**Request Body**:
```json
{
  "session_id": "string",
  "message": "string",
  "user_role": "trainee" | "instructor" | "operator" | "support_engineer",
  "context": {
    "module": "string (optional)",
    "channel": "string (optional)"
  }
}
```

**Response**:
```json
{
  "answer": "string",
  "kb_references": [
    {
      "id": "string",
      "title": "string",
      "excerpt": "string"
    }
  ],
  "confidence": 0.85,
  "tier": "TIER_1",
  "severity": "MEDIUM",
  "needs_escalation": false,
  "guardrail": {
    "blocked": false,
    "reason": null
  },
  "ticket_id": "TICKET-0001" | null
}
```

**Example**:
```bash
curl -X POST https://bayinfotech-test.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-123",
    "message": "I cannot access the lab",
    "user_role": "trainee",
    "context": {
      "module": "lab-1",
      "channel": "self-service-portal"
    }
  }'
```

**Status Codes**:
- `200 OK`: Success
- `422 Unprocessable Entity`: Invalid request body
- `500 Internal Server Error`: Server error

---

### Tickets API

#### `POST /api/tickets`

Create a new support ticket.

**Request Body**:
```json
{
  "session_id": "string",
  "subject": "string",
  "description": "string",
  "tier": "TIER_0" | "TIER_1" | "TIER_2" | "TIER_3" | "TIER_4",
  "severity": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "user_role": "trainee" | "instructor" | "operator" | "support_engineer",
  "context": {},
  "ai_analysis": {}
}
```

**Response**:
```json
{
  "id": "TICKET-0001",
  "session_id": "string",
  "subject": "string",
  "description": "string",
  "tier": "TIER_1",
  "severity": "MEDIUM",
  "status": "OPEN",
  "user_role": "trainee",
  "context": {},
  "ai_analysis": {},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes**:
- `201 Created`: Ticket created successfully
- `422 Unprocessable Entity`: Invalid request body
- `500 Internal Server Error`: Server error

---

#### `GET /api/tickets`

List all tickets with optional filters.

**Query Parameters**:
- `status` (optional): Filter by status (OPEN, IN_PROGRESS, RESOLVED, CLOSED)
- `tier` (optional): Filter by tier (TIER_0, TIER_1, etc.)
- `severity` (optional): Filter by severity (LOW, MEDIUM, HIGH, CRITICAL)
- `limit` (optional, default: 50): Maximum number of tickets to return

**Response**:
```json
[
  {
    "id": "TICKET-0001",
    "session_id": "string",
    "subject": "string",
    "description": "string",
    "tier": "TIER_1",
    "severity": "MEDIUM",
    "status": "OPEN",
    "user_role": "trainee",
    "context": {},
    "ai_analysis": {},
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

**Example**:
```bash
curl https://bayinfotech-test.onrender.com/api/tickets?status=OPEN&severity=HIGH
```

---

#### `GET /api/tickets/{ticket_id}`

Get a specific ticket by ID.

**Response**:
```json
{
  "id": "TICKET-0001",
  "session_id": "string",
  "subject": "string",
  "description": "string",
  "tier": "TIER_1",
  "severity": "MEDIUM",
  "status": "OPEN",
  "user_role": "trainee",
  "context": {},
  "ai_analysis": {},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes**:
- `200 OK`: Success
- `404 Not Found`: Ticket not found
- `500 Internal Server Error`: Server error

---

#### `PATCH /api/tickets/{ticket_id}`

Update a ticket's status, tier, or severity.

**Request Body**:
```json
{
  "status": "IN_PROGRESS" | "RESOLVED" | "CLOSED" (optional),
  "tier": "TIER_0" | "TIER_1" | ... (optional),
  "severity": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" (optional)
}
```

**Response**:
```json
{
  "id": "TICKET-0001",
  "status": "IN_PROGRESS",
  ...
}
```

**Status Codes**:
- `200 OK`: Success
- `404 Not Found`: Ticket not found
- `422 Unprocessable Entity`: Invalid request body
- `500 Internal Server Error`: Server error

---

### Metrics API

#### `GET /api/metrics/summary`

Get summary metrics for the help desk.

**Response**:
```json
{
  "total_conversations": 150,
  "total_tickets": 45,
  "deflection_rate": 0.70,
  "avg_confidence": 0.82,
  "guardrail_activations": 3,
  "tickets_by_tier": {
    "TIER_0": 10,
    "TIER_1": 20,
    "TIER_2": 10,
    "TIER_3": 5
  },
  "tickets_by_severity": {
    "LOW": 15,
    "MEDIUM": 20,
    "HIGH": 8,
    "CRITICAL": 2
  }
}
```

---

#### `GET /api/metrics/trends`

Get trend data for conversations and tickets.

**Query Parameters**:
- `period` (optional, default: 7): Number of days to include

**Response**:
```json
{
  "conversation_volume": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "value": 25
    }
  ],
  "ticket_volume": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "value": 8
    }
  ],
  "deflection_rate": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "value": 0.68
    }
  ],
  "avg_confidence": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "value": 0.81
    }
  ]
}
```

---

#### `GET /api/metrics/deflection`

Get ticket deflection metrics.

**Response**:
```json
{
  "total_conversations": 150,
  "tickets_created": 45,
  "deflection_rate": 0.70,
  "deflected_by_tier": {
    "TIER_0": 80,
    "TIER_1": 25
  }
}
```

---

#### `GET /api/metrics/guardrails`

Get guardrail activation metrics.

**Response**:
```json
{
  "total_activations": 3,
  "activations_by_type": {
    "UNAUTHORIZED_ACCESS": 2,
    "DISABLE_LOGGING": 1
  },
  "recent_events": [
    {
      "id": "uuid",
      "session_id": "string",
      "trigger_type": "UNAUTHORIZED_ACCESS",
      "severity": "CRITICAL",
      "user_message": "string",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

## Error Responses

All endpoints may return the following error format:

```json
{
  "detail": "Error message"
}
```

**Common Status Codes**:
- `400 Bad Request`: Invalid request
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

---

## Rate Limiting

Currently handled by Render platform. No explicit rate limits enforced at application level.

---

## CORS

Allowed origins:
- `http://localhost:5173`
- `http://localhost:3000`
- `http://bayinfotech-test-r9bncip32-kunal63s-projects.vercel.app`

---

## Interactive Documentation

Visit `https://bayinfotech-test.onrender.com/docs` for interactive Swagger UI documentation.
