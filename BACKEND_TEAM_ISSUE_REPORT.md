# 🐛 Backend Issue: Folder Indexing Failing Silently

## Issue Summary
Folder indexing is failing but no error message is being stored or returned to the frontend. The folder status changes to "failed" but the `error_message` field is null/empty.

## Current Behavior
1. User uploads documents to folder → ✅ Works (status: "parsed")
2. User clicks "Index Selected Folder" → Frontend calls `POST /folders/{folder_id}/index`
3. Backend receives request → ✅ Works
4. Indexing job runs → ❌ Fails silently
5. Folder status becomes "failed" → ✅ Status updated
6. Error message is NOT stored → ❌ Problem

## API Response Analysis

### Status Check Response:
```json
{
  "folder_id": "b98fba0e-8775-4901-818b-21c725e98d0f",
  "name": "Eternalgy 2",
  "status": "failed",
  "last_indexed": null,
  "document_count": 2
}
```

**Missing:** `error_message` field is not present or is null

## What Backend Team Needs to Fix

### 1. Store Error Messages in Database
When indexing fails, capture the exception and store it:

```python
# In your indexing job/task
try:
    # ... indexing logic ...
    folder.status = "ready"
    folder.last_indexed = datetime.utcnow()
except Exception as e:
    folder.status = "failed"
    folder.error_message = str(e)  # ← ADD THIS
    folder.error_traceback = traceback.format_exc()  # ← OPTIONAL BUT HELPFUL
    logger.error(f"Indexing failed for folder {folder_id}: {e}", exc_info=True)
finally:
    db.commit()
```

### 2. Return Error in Status Endpoint
Update `GET /folders/{folder_id}/status` to include error details:

```python
return {
    "folder_id": folder.folder_id,
    "name": folder.name,
    "status": folder.status,
    "last_indexed": folder.last_indexed,
    "document_count": folder.document_count,
    "error_message": folder.error_message,  # ← ADD THIS
    "error_timestamp": folder.error_timestamp  # ← OPTIONAL
}
```

### 3. Add Database Column (if not exists)
Ensure your `folders` table has:

```sql
ALTER TABLE folders ADD COLUMN error_message TEXT;
ALTER TABLE folders ADD COLUMN error_timestamp TIMESTAMP;
```

Or in your SQLAlchemy model:
```python
class Folder(Base):
    # ... existing fields ...
    error_message = Column(Text, nullable=True)
    error_timestamp = Column(DateTime, nullable=True)
```

### 4. Improve Logging
Add detailed logging in the indexing endpoint:

```python
@app.post("/folders/{folder_id}/index")
async def index_folder(folder_id: str, payload: IndexRequest):
    logger.info(f"Indexing request received for folder {folder_id}")
    logger.info(f"Method: {payload.method}")
    
    try:
        # Start indexing job
        job = start_indexing_job(folder_id, payload.method)
        logger.info(f"Indexing job started: {job.id}")
        
        return {
            "job_id": job.id,
            "status": "pending",
            "message": f"Indexing job created for folder '{folder.name}'"
        }
    except Exception as e:
        logger.error(f"Failed to start indexing job: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

## Diagnostic Questions for Backend Team

Please check and answer:

1. **Is the indexing endpoint being called?**
   - Check logs for: `POST /folders/{folder_id}/index`
   - What HTTP status code is returned?

2. **What error occurs during indexing?**
   - Check logs for exceptions/stack traces
   - Common issues:
     - Missing `OPENAI_API_KEY` or other LLM API keys
     - GraphRAG configuration missing or invalid
     - Background worker (Celery) not running
     - Database connection issues
     - File system permissions

3. **Is the background worker running?**
   - If using Celery: Is the worker process running?
   - Check Railway for worker process status
   - Verify `Procfile` or `railway.json` has worker defined

4. **Are environment variables set?**
   Required variables:
   - `OPENAI_API_KEY` (or your LLM provider key)
   - `DATABASE_URL`
   - `CELERY_BROKER_URL` (if using Celery)
   - Any GraphRAG-specific config

5. **Does GraphRAG configuration exist?**
   - Check for `settings.yaml` or similar config files
   - Verify paths are correct
   - Ensure all required dependencies are installed

## Expected Behavior After Fix

1. User clicks "Index Selected Folder"
2. Backend starts indexing job
3. If job fails:
   - Error is logged to console/logs
   - Error is stored in database (`error_message` field)
   - Status endpoint returns error details
   - Frontend displays error to user
4. If job succeeds:
   - Status changes to "ready"
   - `last_indexed` timestamp is set
   - Documents become queryable

## Test Case

After implementing fixes, test with:

```bash
# 1. Create folder
POST /folders/create
{"name": "Test Folder"}

# 2. Upload document
POST /folders/{folder_id}/upload
[file upload]

# 3. Trigger indexing
POST /folders/{folder_id}/index
{"method": "fast"}

# 4. Check status (should show error if it fails)
GET /folders/{folder_id}/status

# Expected response if failed:
{
  "folder_id": "...",
  "name": "Test Folder",
  "status": "failed",
  "error_message": "OpenAI API key not configured",  # ← Should be present
  "document_count": 1
}
```

## Frontend Status

✅ Frontend is correctly:
- Calling the indexing endpoint
- Handling errors
- Displaying status
- Showing error messages (when provided by backend)

❌ Backend is NOT:
- Storing error messages when indexing fails
- Returning error details in status endpoint

## Priority: HIGH
Users cannot use the system until indexing works. This is a blocking issue.

## Contact
If you need more information or have questions, please let me know.
