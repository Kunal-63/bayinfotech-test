# Testing the New API Rate Limiting KB Document

## Document Created

✅ **File**: `11-api-rate-limiting.md`  
✅ **Location**: `d:\Github Repo\bayinfotech-sample\backend\app\kb\documents\`  
✅ **KB ID**: `kb-api-rate-limiting`  
✅ **Topic**: API Rate Limiting and Quota Management

---

## Next Steps to Test

### Step 1: Ingest the Document

```bash
cd d:\Github Repo\bayinfotech-sample\backend

# Run the ingestion script
python -m app.kb.ingestion --ingest
```

**Expected Output:**
```
INFO - kb_ingestion_started
INFO - kb_files_found - count=12
INFO - generating_embedding - kb_id=kb-api-rate-limiting
INFO - kb_document_ingested - kb_id=kb-api-rate-limiting - title=API Rate Limiting and Quota Management
INFO - kb_ingestion_completed - total_documents=12
```

### Step 2: Start the Backend Server

```bash
uvicorn app.main:app --reload
```

### Step 3: Test Questions

Ask these questions to verify the KB is being used:

#### ✅ Test Question 1: Basic Rate Limits
**Question**: "What are the API rate limits for a Trainee user?"

**Expected Response Should Include**:
- 60 requests per minute
- 1,000 requests per hour
- 10,000 daily quota
- Reference to `kb-api-rate-limiting`

#### ✅ Test Question 2: Error Handling
**Question**: "I'm getting a 429 error from the API, how do I fix it?"

**Expected Response Should Include**:
- Explanation of HTTP 429 (Too Many Requests)
- Exponential backoff code example
- Check `Retry-After` header
- Implement request spacing
- Reference to `kb-api-rate-limiting`

#### ✅ Test Question 3: Quota Check
**Question**: "How do I check my current API quota usage?"

**Expected Response Should Include**:
- `curl` command to `/api/quota` endpoint
- Explanation of response fields
- Monitoring best practices
- Reference to `kb-api-rate-limiting`

#### ✅ Test Question 4: Premium Tiers
**Question**: "What's the difference between Bronze and Gold premium tiers for API limits?"

**Expected Response Should Include**:
- Bronze: 1.5x multiplier
- Gold: 3x multiplier
- Comparison of limits
- Reference to `kb-api-rate-limiting`

#### ✅ Test Question 5: Quota Increase
**Question**: "How can I request an API quota increase?"

**Expected Response Should Include**:
- Temporary vs permanent increase options
- Upgrade to premium tier
- Contact sales for custom enterprise quota
- Reference to `kb-api-rate-limiting`

#### ✅ Test Question 6: Best Practices
**Question**: "What are the best practices to avoid hitting API rate limits?"

**Expected Response Should Include**:
- Implement exponential backoff
- Use request batching
- Cache API responses
- Use webhooks instead of polling
- Code examples from the KB
- Reference to `kb-api-rate-limiting`

---

## Unique Identifiers to Look For

When the chatbot uses this KB, you should see these **unique identifiers** in the response:

### 1. Specific Numbers
- **60** requests per minute (Trainee)
- **1,000** requests per hour (Trainee)
- **10,000** daily quota (Trainee)
- **1.5x** (Bronze multiplier)
- **2x** (Silver multiplier)
- **3x** (Gold multiplier)
- **5x** (Platinum multiplier)

### 2. Specific Code Examples
- Python code with `api_call_with_retry` function
- Exponential backoff implementation
- Request batching examples
- Caching with `@lru_cache`

### 3. Specific Endpoints
- `/api/quota` endpoint
- `/api/labs/batch` endpoint
- `/api/webhooks` endpoint

### 4. Specific Headers
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`
- `Retry-After`

### 5. Date Reference
- Document created on **2025-11-29**
- Note mentioning "TEST KNOWLEDGE BASE DOCUMENT"

---

## Verification Checklist

- [ ] Document ingested successfully (check logs)
- [ ] Backend server running
- [ ] Test Question 1: Rate limits for Trainee ✅
- [ ] Test Question 2: 429 error handling ✅
- [ ] Test Question 3: Quota check ✅
- [ ] Test Question 4: Premium tiers ✅
- [ ] Test Question 5: Quota increase ✅
- [ ] Test Question 6: Best practices ✅
- [ ] Response includes unique identifiers (numbers, code, endpoints)
- [ ] Response references `kb-api-rate-limiting`

---

## Troubleshooting

### If chatbot doesn't reference the new KB:

1. **Verify ingestion**:
   ```bash
   sqlite3 app.db
   SELECT title, doc_metadata->>'kb_id' FROM kb_documents WHERE title LIKE '%Rate%';
   .exit
   ```

2. **Check embedding was generated**:
   ```bash
   sqlite3 app.db
   SELECT title, length(embedding) FROM kb_documents WHERE title LIKE '%Rate%';
   .exit
   ```

3. **Try more specific questions** that match the KB content exactly

4. **Re-ingest if needed**:
   ```bash
   # Delete and re-ingest
   sqlite3 app.db
   DELETE FROM kb_documents WHERE title = 'API Rate Limiting and Quota Management';
   .exit
   
   python -m app.kb.ingestion --ingest
   ```

---

## Success Criteria

✅ **The test is successful if**:
1. Chatbot answers questions about API rate limiting
2. Response includes specific numbers (60, 1000, 10000, etc.)
3. Response includes code examples from the KB
4. Response references `kb-api-rate-limiting` document
5. Response does NOT say "This information is not covered in the knowledge base"

---

## Quick Commands Reference

```bash
# Navigate to backend
cd d:\Github Repo\bayinfotech-sample\backend

# Ingest KB documents
python -m app.kb.ingestion --ingest

# Start server
uvicorn app.main:app --reload

# Check database
sqlite3 app.db
SELECT title FROM kb_documents;
.exit
```

---

**Ready to test!** Follow the steps above and verify the chatbot uses the new KB document correctly.
