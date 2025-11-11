# GraphRAG Chatbot - Frontend (Gradio UI)

Standalone Gradio web interface for the GraphRAG Chatbot API.

## Overview

This is the **frontend-only** deployment that connects to a separate backend API service. It provides a user-friendly web interface with 3 tabs:

- 🗄️ **Knowledge Vault** - Manage folders and upload documents
- 👤 **Agents** - Configure multi-folder agents
- 💬 **Chat Playground** - Interactive chat with agents

## Architecture

```
User Browser → Gradio UI (This Service) → Backend API → GraphRAG + Database
```

## Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r frontend-requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.frontend.sample .env
   # Edit .env with your backend API URL
   ```

3. **Run the UI:**
   ```bash
   python apps/ui/app.py
   ```

4. **Access:**
   ```
   http://localhost:7860
   ```

### Railway Deployment

#### Prerequisites

1. **Backend API deployed** - You need a running backend service
   - Deploy from `Added-GUI` branch
   - Note the Railway URL (e.g., `https://graphrag-api.railway.app`)

#### Deploy Frontend

1. **Create new Railway service:**
   - Name: "GraphRAG-UI" or similar
   - Connect to your GitHub repository
   - Select branch: `gradio-frontend`

2. **Configure build:**
   - Build Command: (leave default)
   - Dockerfile Path: `Dockerfile.frontend`

3. **Set environment variables:**
   ```bash
   API_BASE_URL=https://your-backend-api.railway.app
   ADMIN_TOKEN=your-admin-token-from-backend
   ```

4. **Deploy:**
   - Railway will auto-deploy
   - Access your UI at the assigned Railway URL

## Environment Variables

### Required

- **`API_BASE_URL`** - Backend API URL
  - Example: `https://graphrag-api.railway.app`
  - Must be accessible from the frontend service

- **`ADMIN_TOKEN`** - Admin authentication token
  - Must match the backend's `ADMIN_TOKEN`
  - Used for folder creation, indexing, etc.

### Optional

- **`PORT`** - Gradio server port (default: 7860)
  - Railway will override this automatically

## Features

### Knowledge Vault Tab

- Create and manage knowledge folders
- Upload documents (PDF, DOCX, TXT, MD, CSV, XLSX, images)
- Trigger folder indexing
- View folder status and document counts
- Delete folders (with safety checks)

### Agents Tab

- Create multi-folder agents
- Configure agent settings:
  - Name and role instructions
  - Folder access (select multiple folders)
  - Retrieval method (global/local)
  - LLM model and temperature
  - Top-K results
- List and manage agents
- Delete agents

### Chat Playground Tab

- Select an agent to chat with
- Send messages and receive responses
- View conversation history
- Clear chat history
- Session management
- Real-time streaming responses

## API Communication

The frontend makes HTTP requests to the backend API:

```python
# Example: Create folder
response = httpx.post(
    f"{API_BASE}/folders/create",
    json={"name": "My Folder"},
    headers={"X-Admin-Token": ADMIN_TOKEN}
)
```

### Endpoints Used

- `POST /folders/create` - Create folder
- `GET /folders/list` - List folders
- `DELETE /folders/{id}` - Delete folder
- `POST /folders/{id}/upload` - Upload document
- `POST /folders/{id}/index` - Trigger indexing
- `POST /agents/create` - Create agent
- `GET /agents/list` - List agents
- `DELETE /agents/{id}` - Delete agent
- `POST /chat/{agent_id}/message` - Send chat message
- `GET /chat/{agent_id}/history` - Get chat history

## Troubleshooting

### Cannot connect to backend

**Error:** Connection refused or timeout

**Solutions:**
1. Verify `API_BASE_URL` is correct
2. Check backend service is running
3. Ensure backend allows CORS from frontend domain
4. Check network connectivity

### Authentication errors

**Error:** 401 Unauthorized

**Solutions:**
1. Verify `ADMIN_TOKEN` matches backend
2. Check token is set in environment variables
3. Ensure backend has `ADMIN_TOKEN` configured

### UI not loading

**Error:** Gradio fails to start

**Solutions:**
1. Check Railway logs for errors
2. Verify `frontend-requirements.txt` installed correctly
3. Ensure `PORT` is not conflicting
4. Check Railway assigned PORT is being used

## Development

### Project Structure

```
gradio-frontend/
├── apps/
│   └── ui/
│       └── app.py              # Gradio UI application
├── frontend-requirements.txt    # Frontend dependencies
├── Dockerfile.frontend         # Frontend Docker image
├── .env.frontend.sample        # Environment template
└── README.frontend.md          # This file
```

### Adding Features

1. **Modify UI:**
   ```bash
   # Edit apps/ui/app.py
   # Test locally
   python apps/ui/app.py
   ```

2. **Commit and push:**
   ```bash
   git add apps/ui/app.py
   git commit -m "feat: add new UI feature"
   git push origin gradio-frontend
   ```

3. **Railway auto-deploys** the changes

### Testing Locally

```bash
# Set backend URL
export API_BASE_URL=http://localhost:8000

# Or use production backend
export API_BASE_URL=https://your-backend.railway.app

# Run UI
python apps/ui/app.py
```

## Deployment Checklist

- [ ] Backend API deployed and accessible
- [ ] Backend URL noted (e.g., `https://graphrag-api.railway.app`)
- [ ] Admin token from backend noted
- [ ] Railway service created for frontend
- [ ] Branch set to `gradio-frontend`
- [ ] Dockerfile path set to `Dockerfile.frontend`
- [ ] Environment variables configured:
  - [ ] `API_BASE_URL`
  - [ ] `ADMIN_TOKEN`
- [ ] Deployment successful
- [ ] UI accessible at Railway URL
- [ ] Can create folders
- [ ] Can create agents
- [ ] Can chat with agents

## Cost Estimate

**Railway Pricing:**
- Frontend service: ~$5/month (lightweight, no database)
- No persistent volume needed (stateless)

**Total:** ~$5/month for frontend + backend costs separately

## Support

For issues:
1. Check Railway logs: `railway logs`
2. Verify backend connectivity
3. Check environment variables
4. Review API documentation

## Related Documentation

- **Backend API:** See `Added-GUI` branch README
- **API Endpoints:** See `AGENT_API_USAGE.md` and `CHAT_API_USAGE.md`
- **Deployment Guide:** See `SEPARATE_FRONTEND_BACKEND.md`

## License

MIT
