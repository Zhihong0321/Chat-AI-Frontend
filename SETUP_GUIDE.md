# Frontend Separation Guide

## What Happened

We separated the Gradio frontend into its own independent project to avoid confusion with branch-based deployment.

## Current Status

✅ **Files copied to `E:\Chat-AI-Frontend\`:**
- `apps/ui/` - Gradio application code
- `requirements.txt` (from frontend-requirements.txt)
- `Dockerfile` (from Dockerfile.frontend)
- `.env.sample` (from .env.frontend.sample)
- `.gitignore`
- `README.md` (from README.frontend.md)

## What Still Needs to Be Done in `E:\Chat-AI-Frontend\`

### 1. Create Missing Files

Create `start.sh`:
```bash
#!/bin/bash
set -e

echo "Starting Gradio Frontend..."
echo "API Backend: ${API_BASE_URL:-http://localhost:8000}"
echo "Port: ${PORT:-7860}"

# Start Gradio
python -m apps.ui.app
```

Create `apps/__init__.py`:
```python
# Empty init file
```

### 2. Create Railway Configuration

Create `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "bash start.sh",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 3. Update Dockerfile if Needed

The Dockerfile should look like this:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY apps/ ./apps/
COPY start.sh .

# Make start script executable
RUN chmod +x start.sh

# Expose Gradio default port
EXPOSE 7860

# Start command
CMD ["bash", "start.sh"]
```

### 4. Initialize Git Repository

```bash
cd E:\Chat-AI-Frontend
git init
git add .
git commit -m "Initial commit: Gradio frontend separated from backend"
```

### 5. Create GitHub Repository

```bash
# Create repo on GitHub (use GitHub CLI or web interface)
gh repo create Chat-AI-Frontend --public --source=. --remote=origin

# Or manually:
# 1. Go to https://github.com/new
# 2. Create repo named "Chat-AI-Frontend"
# 3. Then:
git remote add origin https://github.com/YOUR_USERNAME/Chat-AI-Frontend.git
git branch -M main
git push -u origin main
```

### 6. Deploy to Railway

1. Go to Railway dashboard
2. Create new project
3. Connect to GitHub repo `Chat-AI-Frontend`
4. Set environment variables:
   - `API_BASE_URL` = Your backend API URL (e.g., https://your-backend.railway.app)
   - `ADMIN_TOKEN` = Same as backend admin token
   - `PORT` = 7860 (or Railway will auto-assign)
5. Deploy!

## Environment Variables Needed

```env
# Backend API connection
API_BASE_URL=http://localhost:8000

# Admin token (must match backend)
ADMIN_TOKEN=your-secure-token-here

# Port (Railway auto-assigns, local default is 7860)
PORT=7860
```

## Architecture

```
Frontend (E:\Chat-AI-Frontend\)
    ↓ HTTP calls
Backend (E:\EE-RAG\)
    ↓ Uses
OpenAI API + GraphRAG
```

The frontend is a pure UI layer that makes HTTP requests to the backend API. No direct code sharing needed.

## Benefits of This Separation

1. ✅ No branch confusion - each project has its own repo
2. ✅ Clear separation of concerns
3. ✅ Independent deployment cycles
4. ✅ Easier for AI assistants to understand context
5. ✅ No risk of accidentally mixing frontend/backend code

## Backend Repository

The backend remains at `E:\EE-RAG\` with:
- Branch: `master` (main backend)
- GitHub: https://github.com/Zhihong0321/Eternalgy-RAG-AI.git
- Railway: Connected to `master` branch

## Testing Locally

### Backend:
```bash
cd E:\EE-RAG
python -m uvicorn apps.api.main:app --reload --port 8000
```

### Frontend:
```bash
cd E:\Chat-AI-Frontend
set API_BASE_URL=http://localhost:8000
python -m apps.ui.app
```

Then open http://localhost:7860

## Important Notes

- Frontend calls backend via HTTP - no direct imports
- Both need to be running for full functionality
- Frontend needs `API_BASE_URL` pointing to backend
- Backend needs CORS enabled for frontend domain (already configured)

## Next Steps for AI Assistant

When you open `E:\Chat-AI-Frontend\` workspace:

1. Read this guide
2. Create the missing files listed above
3. Initialize git and push to GitHub
4. Help user deploy to Railway
5. Test the connection between frontend and backend

## Files Already Copied

- ✅ apps/ui/app.py (main Gradio application)
- ✅ apps/ui/__init__.py
- ✅ requirements.txt (Gradio + httpx + python-dotenv)
- ✅ Dockerfile (Python 3.11 slim)
- ✅ .env.sample (environment variable template)
- ✅ .gitignore (Python + Railway ignores)
- ✅ README.md (frontend-specific documentation)

## Contact

If issues arise, refer back to the backend repository for API documentation and schemas.
