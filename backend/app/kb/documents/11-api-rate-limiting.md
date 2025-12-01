---
kb_id: kb-api-rate-limiting
title: API Rate Limiting and Quota Management
version: 1.0
last_updated: 2025-11-29
tier: TIER_1
severity: MEDIUM
tags: [api, rate-limiting, quota, throttling, 429-error]
---

# API Rate Limiting and Quota Management

This document describes the API rate limiting policies, quota management, and troubleshooting steps for CyberLab platform API access.

> **Note:** This is a TEST KNOWLEDGE BASE DOCUMENT created on 2025-11-29 for testing purposes. If you see this referenced in chatbot responses, it means the KB ingestion and retrieval is working correctly!

## Overview

The CyberLab platform enforces API rate limits to ensure fair usage and system stability. All API endpoints are subject to rate limiting based on user role and subscription tier.

## Rate Limit Tiers

### Standard Rate Limits by Role

| User Role | Requests per Minute | Requests per Hour | Daily Quota |
|-----------|---------------------|-------------------|-------------|
| Trainee | 60 | 1,000 | 10,000 |
| Instructor | 120 | 2,500 | 25,000 |
| Operator | 300 | 10,000 | 100,000 |
| Support Engineer | 500 | 20,000 | 200,000 |
| Admin | 1,000 | 50,000 | 500,000 |

### Premium Tier Multipliers

Users with premium subscriptions receive the following multipliers:
- **Bronze**: 1.5x all limits
- **Silver**: 2x all limits
- **Gold**: 3x all limits
- **Platinum**: 5x all limits

## Common Symptoms

### 1. HTTP 429 - Too Many Requests

**Symptom:**
User reports: "I'm getting 429 errors when calling the API"

**Response Headers:**
```
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1701234567
Retry-After: 45
```

### 2. Quota Exceeded

**Symptom:**
User reports: "API returns 'quota exceeded' error"

**Response:**
```json
{
  "error": "quota_exceeded",
  "message": "Daily API quota exceeded",
  "quota_limit": 10000,
  "quota_used": 10000,
  "reset_time": "2025-11-30T00:00:00Z"
}
```

---

## Troubleshooting Steps

### 1. Check Current Rate Limit Status

Instruct the user to check the response headers from their API calls:

```bash
curl -I https://api.cyberlab.local/v1/labs \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Key Headers to Check:**
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Unix timestamp when limit resets
- `Retry-After`: Seconds to wait before retrying

### 2. Verify User Role and Tier

Ask the user:
1. What is your current role? (Trainee, Instructor, etc.)
2. Do you have a premium subscription?
3. When did the rate limiting start occurring?

### 3. Self-Service Solutions (Tier 0/Tier 1)

#### Solution A: Implement Exponential Backoff

Provide this code example for handling rate limits:

```python
import time
import requests

def api_call_with_retry(url, headers, max_retries=3):
    """Make API call with exponential backoff on rate limit."""
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        
        elif response.status_code == 429:
            # Rate limited - check retry-after header
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
        
        else:
            # Other error
            response.raise_for_status()
    
    raise Exception("Max retries exceeded")

# Usage
url = "https://api.cyberlab.local/v1/labs"
headers = {"Authorization": "Bearer YOUR_TOKEN"}
data = api_call_with_retry(url, headers)
```

#### Solution B: Implement Request Batching

Instead of making individual API calls, batch requests:

```python
# Instead of this (60 individual calls):
for lab_id in range(1, 61):
    response = requests.get(f"/api/labs/{lab_id}")

# Do this (1 batched call):
lab_ids = list(range(1, 61))
response = requests.post("/api/labs/batch", json={"ids": lab_ids})
```

#### Solution C: Cache API Responses

Implement caching to reduce API calls:

```python
import time
from functools import lru_cache

@lru_cache(maxsize=100)
def get_lab_info(lab_id):
    """Cached API call - returns cached result if called within cache lifetime."""
    response = requests.get(f"https://api.cyberlab.local/v1/labs/{lab_id}")
    return response.json()

# This will only make 1 API call, not 5
for i in range(5):
    data = get_lab_info(123)  # Same lab_id = cached result
```

#### Solution D: Check for Infinite Loops

Verify the user's code isn't making unintended API calls:

```python
# BAD - Infinite loop making API calls
while True:
    status = requests.get("/api/status")  # This will hit rate limit!
    if status.json()["ready"]:
        break

# GOOD - Add delay between checks
import time
while True:
    status = requests.get("/api/status")
    if status.json()["ready"]:
        break
    time.sleep(5)  # Wait 5 seconds between checks
```

---

## Rate Limit Best Practices

### 1. Monitor Your Usage

Check your current quota usage:

```bash
curl https://api.cyberlab.local/v1/quota \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "role": "trainee",
  "tier": "standard",
  "limits": {
    "per_minute": 60,
    "per_hour": 1000,
    "per_day": 10000
  },
  "usage": {
    "current_minute": 45,
    "current_hour": 823,
    "current_day": 7234
  },
  "reset_times": {
    "minute": "2025-11-29T23:29:00Z",
    "hour": "2025-11-30T00:00:00Z",
    "day": "2025-11-30T00:00:00Z"
  }
}
```

### 2. Use Webhooks Instead of Polling

Instead of polling for status updates (which consumes quota):

```python
# BAD - Polling every second
while True:
    status = requests.get("/api/labs/123/status")
    if status.json()["state"] == "running":
        break
    time.sleep(1)  # 60 API calls per minute!
```

Use webhooks to receive notifications:

```python
# GOOD - Register webhook
webhook_url = "https://your-server.com/webhook"
requests.post("/api/webhooks", json={
    "url": webhook_url,
    "events": ["lab.started", "lab.stopped"]
})
# Now you'll receive notifications without polling!
```

### 3. Optimize Bulk Operations

Use bulk endpoints when available:

```bash
# Instead of 100 individual calls:
# GET /api/labs/1
# GET /api/labs/2
# ...
# GET /api/labs/100

# Use bulk endpoint (1 call):
POST /api/labs/bulk
{
  "ids": [1, 2, 3, ..., 100]
}
```

---

## Escalation Criteria

### Escalate to Tier 2 (Support Engineer) if:

1. User has implemented all best practices but still hits rate limits during normal usage
2. User believes their quota is incorrect for their role/tier
3. Multiple users from the same organization report rate limiting issues
4. Rate limit errors occur even when usage is well below documented limits

### Information to Provide When Escalating:

- User role and subscription tier
- Current quota limits (from `/api/quota` endpoint)
- Recent usage patterns (requests per minute/hour)
- Specific API endpoints being called
- Code snippet showing API usage pattern
- Timestamp when rate limiting started
- Any error messages or response headers

---

## Requesting Quota Increase

### Temporary Quota Increase

For short-term needs (e.g., running a large batch job):

1. Submit a request through the support portal
2. Provide justification and estimated duration
3. Specify required quota (requests per hour/day)
4. Approval typically within 4 business hours

### Permanent Quota Increase

For ongoing higher usage needs:

1. **Option A**: Upgrade to premium tier (Bronze/Silver/Gold/Platinum)
2. **Option B**: Request custom enterprise quota
   - Contact sales team
   - Provide usage projections
   - Custom pricing based on needs

---

## API Rate Limit Error Codes

| Error Code | Description | Solution |
|------------|-------------|----------|
| 429 | Too many requests | Wait for rate limit reset, implement backoff |
| QUOTA_EXCEEDED | Daily quota exceeded | Wait until midnight UTC or upgrade tier |
| BURST_LIMIT | Too many requests in short burst | Implement request spacing |
| CONCURRENT_LIMIT | Too many concurrent requests | Reduce parallel requests |

---

## Monitoring and Alerts

### Set Up Quota Alerts

Configure alerts when approaching quota limits:

```python
import requests

def check_quota_and_alert(threshold=0.8):
    """Alert when quota usage exceeds threshold (default 80%)."""
    response = requests.get(
        "https://api.cyberlab.local/v1/quota",
        headers={"Authorization": "Bearer YOUR_TOKEN"}
    )
    data = response.json()
    
    daily_usage = data["usage"]["current_day"]
    daily_limit = data["limits"]["per_day"]
    usage_percent = daily_usage / daily_limit
    
    if usage_percent >= threshold:
        print(f"WARNING: {usage_percent*100:.1f}% of daily quota used!")
        print(f"Used: {daily_usage} / {daily_limit}")
        # Send alert email, Slack notification, etc.
        return True
    
    return False

# Run this periodically (e.g., every hour)
check_quota_and_alert()
```

---

## Special Cases

### 1. Automated Testing and CI/CD

For automated testing pipelines that need higher limits:

- Use dedicated service account with Operator role
- Implement proper rate limit handling in tests
- Consider using API mocking for unit tests to avoid quota usage

### 2. Data Migration

For one-time data migration requiring high API usage:

- Request temporary quota increase (see above)
- Use bulk endpoints where available
- Implement checkpointing to resume if quota exceeded

### 3. Real-time Monitoring Dashboards

For dashboards that need frequent updates:

- Use WebSocket connections instead of polling
- Implement client-side caching
- Update only changed data, not full refresh

---

## Related Documents

- See `kb-platform-overview` for general platform information
- See `kb-access-authentication` for API authentication issues
- See `kb-tiering-escalation` for escalation procedures

---

## Testing This KB Document

**To verify this KB is being used by the chatbot, ask questions like:**

1. "What are the API rate limits for a Trainee user?"
2. "I'm getting a 429 error from the API, how do I fix it?"
3. "How do I check my current API quota usage?"
4. "What's the difference between rate limiting and quota?"
5. "How can I request a quota increase?"

**Expected behavior:** The chatbot should reference this document (kb-api-rate-limiting) and provide specific information about rate limits, quotas, and troubleshooting steps.

**Unique identifiers in responses:**
- Specific rate limit numbers (60 req/min for Trainee, 1000 req/hour, etc.)
- Premium tier multipliers (Bronze 1.5x, Silver 2x, etc.)
- Code examples with exponential backoff
- Reference to "2025-11-29" as the document creation date
