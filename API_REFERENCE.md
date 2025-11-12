# Backend API Reference

## Base URL
```
https://eternalgy-rag-ai-production.up.railway.app
```

## Interactive Documentation
- **Swagger UI:** https://eternalgy-rag-ai-production.up.railway.app/docs
- **ReDoc:** https://eternalgy-rag-ai-production.up.railway.app/redoc (if available)

## Health Endpoints

### Simple Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-12T05:20:00Z"
}
```

**No authentication required**

### Detailed Health Check
```http
GET /health/detailed
X-Admin-Token: your-admin-token
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-12T05:20:00Z",
  "components": {
    "api": "healthy",
    "database": "healthy",
    "storage": "healthy",
    "dependencies": "healthy",
    "external_services": "healthy"
  }
}
```

**Requires:** `X-Admin-Token` header

## Folder Management Endpoints

### List Folders
```http
GET /folders/list
```

**Response:**
```json
[
  {
    "folder_id": "uuid",
    "name": "Folder Name",
    "status": "ready",
    "document_count": 5,
    "last_indexed": "2025-11-12T05:00:00Z"
  }
]
```

### Create Folder
```http
POST /folders/create
Content-Type: application/json

{
  "name": "New Folder"
}
```

**Response:**
```json
{
  "folder_id": "uuid",
  "name": "New Folder",
  "status": "not_indexed",
  "created_at": "2025-11-12T05:00:00Z"
}
```

### Get Folder Status
```http
GET /folders/{folder_id}/status
```

**Response:**
```json
{
  "folder_id": "uuid",
  "name": "Folder Name",
  "status": "ready",
  "document_count": 5,
  "last_indexed": "2025-11-12T05:00:00Z",
  "error_message": null
}
```

**Status values:**
- `not_indexed` - Folder created but not indexed
- `parsed` - Documents uploaded and normalized
- `indexing` - Indexing in progress
- `ready` - Indexed and queryable
- `failed` - Indexing failed (check `error_message`)

### Upload Document to Folder
```http
POST /folders/{folder_id}/upload
Content-Type: multipart/form-data

file: [binary file data]
```

**Supported formats:** PDF, DOCX, TXT, MD, CSV, XLSX, PNG, JPG

**Response:**
```json
{
  "doc_id": "uuid",
  "title": "document.pdf",
  "status": "parsed",
  "uploaded_at": "2025-11-12T05:00:00Z"
}
```

### List Documents in Folder
```http
GET /folders/{folder_id}/documents
```

**Response:**
```json
[
  {
    "doc_id": "uuid",
    "title": "document.pdf",
    "status": "parsed",
    "size": 12345,
    "uploaded_at": "2025-11-12T05:00:00Z"
  }
]
```

### Index Folder
```http
POST /folders/{folder_id}/index
Content-Type: application/json

{
  "method": "fast"
}
```

**Methods:**
- `fast` - Quick indexing (recommended)
- `standard` - Comprehensive indexing (slower)

**Response:**
```json
{
  "job_id": "uuid",
  "status": "pending",
  "message": "Indexing job created for folder 'Folder Name'. Processing in background."
}
```

## Agent Management Endpoints

### List Agents
```http
GET /agents/list
```

### Create Agent
```http
POST /agents/create
Content-Type: application/json

{
  "name": "Agent Name",
  "role_instructions": "You are a helpful assistant...",
  "folder_access": ["folder_id_1", "folder_id_2"],
  "retrieval_method": "global",
  "top_k": 10,
  "llm_model": "gpt-4o-mini",
  "temperature": 0.7
}
```

### Get Agent
```http
GET /agents/{agent_id}
```

### Update Agent
```http
PUT /agents/{agent_id}
Content-Type: application/json

{
  "name": "Updated Name",
  "role_instructions": "Updated instructions...",
  "folder_access": ["folder_id_1"],
  "retrieval_method": "local",
  "top_k": 15,
  "llm_model": "gpt-4o",
  "temperature": 0.5
}
```

### Delete Agent
```http
DELETE /agents/{agent_id}
```

## Chat Endpoints

### Send Message
```http
POST /chat/{agent_id}/message
Content-Type: application/json

{
  "message": "What is...?",
  "session_id": "optional-session-id",
  "stream": false
}
```

**Response:**
```json
{
  "response": "Answer to your question...",
  "session_id": "uuid",
  "citations": [
    {
      "folder_name": "Folder Name",
      "title": "document.pdf",
      "snippet": "Relevant text excerpt..."
    }
  ]
}
```

### Get Chat History
```http
GET /chat/{agent_id}/history?session_id=uuid
```

### Clear Chat History
```http
DELETE /chat/{agent_id}/clear?session_id=uuid
```

## Authentication

Most endpoints don't require authentication, but admin endpoints require:

```http
X-Admin-Token: your-admin-token
```

Set in `.env`:
```bash
ADMIN_TOKEN=your-secure-token
```

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message description"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `202` - Accepted (job queued)
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

Check API documentation for current rate limits.

## Frontend Configuration

In your frontend `.env`:

```bash
API_BASE_URL=https://eternalgy-rag-ai-production.up.railway.app
ADMIN_TOKEN=your-admin-token
```

## Testing the API

### Using curl:

```bash
# Health check
curl https://eternalgy-rag-ai-production.up.railway.app/health

# List folders
curl https://eternalgy-rag-ai-production.up.railway.app/folders/list

# Create folder
curl -X POST https://eternalgy-rag-ai-production.up.railway.app/folders/create \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Folder"}'
```

### Using the UI:

The Gradio frontend at your deployment URL provides a user-friendly interface to all these endpoints.

## Support

For issues or questions:
1. Check `/docs` for interactive API documentation
2. Use the "Test API Connection" button in the UI
3. Check backend logs on Railway dashboard
4. Review error messages in the UI status displays
