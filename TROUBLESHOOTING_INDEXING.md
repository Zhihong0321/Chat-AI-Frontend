# Troubleshooting Folder Indexing Failures

## Current Issue
Folder indexing fails with status "failed" after clicking "Index Selected Folder"

## Diagnostic Steps

### 1. Check Backend Logs
The backend is running at: `https://eternalgy-rag-ai-production.up.railway.app`

Go to Railway dashboard and check the backend logs for errors when indexing is triggered.

### 2. Common Causes of Indexing Failure

#### A. Missing Environment Variables
The backend needs these environment variables configured:
```bash
# Required for GraphRAG indexing
OPENAI_API_KEY=sk-...
GRAPHRAG_API_KEY=sk-...  # or whatever LLM provider you're using

# Database
DATABASE_URL=postgresql://...

# Optional but recommended
CELERY_BROKER_URL=redis://...  # For background job processing
```

#### B. Background Worker Not Running
GraphRAG indexing is typically a background job. Check if:
- Celery worker is running (if using Celery)
- Background job processor is configured
- Railway has a worker process defined in `Procfile` or `railway.json`

#### C. GraphRAG Configuration Missing
The backend needs GraphRAG configuration files:
- `settings.yaml` or similar GraphRAG config
- Proper indexing pipeline setup

### 3. Backend Endpoints to Check

Test these endpoints manually:

```bash
# Check if folder exists
GET https://eternalgy-rag-ai-production.up.railway.app/folders/list

# Check folder status
GET https://eternalgy-rag-ai-production.up.railway.app/folders/{folder_id}/status

# Trigger indexing (this is what's failing)
POST https://eternalgy-rag-ai-production.up.railway.app/folders/{folder_id}/index
Content-Type: application/json
{"method": "fast"}
```

### 4. What to Look For in Backend Logs

When you click "Index Selected Folder", look for:
- ❌ `KeyError` or `AttributeError` - Missing configuration
- ❌ `OpenAI API key not found` - Missing API keys
- ❌ `Connection refused` - Database or Redis not accessible
- ❌ `No such file or directory` - Missing GraphRAG config files
- ❌ `Task not registered` - Celery worker not running

### 5. Quick Fixes

#### If API keys are missing:
1. Go to Railway dashboard
2. Add environment variables for your LLM provider
3. Redeploy the backend

#### If worker is not running:
1. Check `Procfile` or `railway.json` in backend repo
2. Ensure worker process is defined:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   worker: celery -A app.worker worker --loglevel=info
   ```
3. Make sure Railway is running both processes

#### If GraphRAG config is missing:
1. Check backend repo for `settings.yaml`
2. Ensure it's properly configured for your use case
3. Verify file paths are correct

### 6. Frontend Improvements (Already Done)
✅ Added detailed error messages
✅ Added "Check Folder Status" button
✅ Added "Test API Connection" button
✅ Show error_message from backend

## Next Steps

1. **Check the backend logs** - This is the most important step
2. Click "Check Folder Status" in the UI to see if backend stored error details
3. Share the error message here so we can diagnose further
4. Check if the backend repository has proper configuration

## Backend API Documentation

The backend API is available at: `https://eternalgy-rag-ai-production.up.railway.app`

**Available Endpoints:**
- `/health` - Simple health check (no auth required)
- `/health/detailed` - Detailed system health (requires X-Admin-Token header)
- `/docs` - Interactive API documentation (Swagger UI)

**Health Check:**
```bash
# Simple health check
curl https://eternalgy-rag-ai-production.up.railway.app/health

# Detailed health check (requires admin token)
curl -H "X-Admin-Token: your-token" https://eternalgy-rag-ai-production.up.railway.app/health/detailed
```

## Backend Repository
If you have access to the backend code repository, we should:
1. Review the `/folders/{folder_id}/index` endpoint implementation
2. Check the indexing job/task implementation
3. Verify GraphRAG configuration
4. Ensure all dependencies are installed
