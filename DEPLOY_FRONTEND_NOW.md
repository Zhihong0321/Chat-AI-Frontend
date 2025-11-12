# Deploy Frontend to Railway - Ready Now! 🚀

## Backend Status: ✅ HEALTHY

Your backend is running at:
**https://eternalgy-rag-ai-production.up.railway.app**

All systems operational. See `BACKEND_HEALTH_CHECK.md` for details.

## Frontend Status: ✅ READY TO DEPLOY

Frontend code is ready at:
**E:\Chat-AI-Frontend\**

GitHub repo: **https://github.com/Zhihong0321/Chat-AI-Frontend**

## Deploy to Railway (5 Minutes)

### Step 1: Go to Railway Dashboard
https://railway.app/dashboard

### Step 2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose `Zhihong0321/Chat-AI-Frontend`
4. Railway will detect the Dockerfile automatically

### Step 3: Set Environment Variables

Click on your service → Variables tab → Add these:

```
API_BASE_URL=https://eternalgy-rag-ai-production.up.railway.app
ADMIN_TOKEN=your-admin-token-here
```

**Important**: Use the SAME `ADMIN_TOKEN` as your backend!

### Step 4: Deploy

Railway will automatically:
1. Build the Docker image
2. Deploy the container
3. Assign a public URL
4. Start the Gradio interface

### Step 5: Get Your Frontend URL

After deployment completes (2-3 minutes):
1. Click on your frontend service
2. Go to "Settings" tab
3. Find "Domains" section
4. Copy your Railway domain (e.g., `chat-ai-frontend-production.up.railway.app`)

## Testing After Deployment

### 1. Check Frontend Health
Visit your frontend URL - you should see the Gradio interface

### 2. Test Connection
1. Go to "Knowledge Vault" tab
2. Try creating a folder
3. If successful, frontend is connected to backend!

### 3. Test Full Workflow
1. Create a folder
2. Upload a document
3. Index the folder
4. Create an agent
5. Chat with the agent

## Architecture After Deployment

```
User Browser
    ↓
Frontend: https://your-frontend.railway.app
    ↓ HTTP API Calls
Backend: https://eternalgy-rag-ai-production.up.railway.app
    ↓
OpenAI + GraphRAG
```

## Troubleshooting

### Frontend Can't Connect to Backend

**Check environment variables:**
```bash
# In Railway frontend service → Variables
API_BASE_URL=https://eternalgy-rag-ai-production.up.railway.app  # ✅ Correct
API_BASE_URL=http://localhost:8000  # ❌ Wrong for production
```

### CORS Errors

Backend already has CORS enabled for all origins. If you see CORS errors:
1. Check backend logs
2. Verify `API_BASE_URL` is correct
3. Ensure backend is healthy: https://eternalgy-rag-ai-production.up.railway.app/healthz

### 404 Errors

Make sure you're using the correct endpoint paths:
- ✅ `/folders/list`
- ✅ `/agents/list`
- ❌ `/folder/list` (wrong)

## Alternative: Railway CLI

If you prefer command line:

```bash
cd E:\Chat-AI-Frontend

# Login to Railway
railway login

# Link to project
railway link

# Set environment variables
railway variables set API_BASE_URL=https://eternalgy-rag-ai-production.up.railway.app
railway variables set ADMIN_TOKEN=your-admin-token

# Deploy
railway up
```

## After Deployment

Update your documentation with the frontend URL:

```markdown
## Live Deployment

- **Backend API**: https://eternalgy-rag-ai-production.up.railway.app
- **Frontend UI**: https://your-frontend.railway.app
- **API Docs**: https://eternalgy-rag-ai-production.up.railway.app/docs
```

## Cost Estimate

Railway free tier includes:
- $5 credit per month
- Both services should fit within free tier for development
- Monitor usage in Railway dashboard

## Next Steps After Deployment

1. ✅ Deploy frontend to Railway
2. ⏳ Test end-to-end workflow
3. ⏳ Upload sample documents
4. ⏳ Create agents
5. ⏳ Share with users!

## Support

If you encounter issues:
1. Check Railway logs (click service → Logs tab)
2. Verify environment variables
3. Test backend health: https://eternalgy-rag-ai-production.up.railway.app/healthz
4. Check `BACKEND_HEALTH_CHECK.md` for API details

---

**Ready to deploy?** Go to https://railway.app/dashboard and follow the steps above!
