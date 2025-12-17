# MVLT AI Service

Minimal FastAPI server for MVLT journaling app AI operations.

## Features

- **Reflection Generation**: Generate empathetic reflections and follow-up questions for journal entries
- **Title Generation**: Auto-generate concise titles for journal entries
- **Entry Chat**: Have conversations about specific journal entries with AI companion
- **Health Check**: Simple endpoint for monitoring server status

## Setup

### 1. Create Virtual Environment

```bash
cd mvlt-ai-service
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Anthropic API key
# ANTHROPIC_API_KEY=sk-ant-...
```

Get your API key from: https://console.anthropic.com/

### 4. Run Server

```bash
python -m app.main
```

Server will start at: http://localhost:8000

## API Documentation

Once the server is running, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Endpoints

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "ok",
  "service": "mvlt-ai-service",
  "version": "0.1.0"
}
```

### Generate Reflection

```bash
POST /reflection
Content-Type: application/json

{
  "content": "Today I felt anxious about my presentation...",
  "companion": {
    "name": "Yuzu",
    "avatar": "🐨",
    "traits": ["Friendly", "Supportive"]
  }
}
```

Response:
```json
{
  "reflection": "I hear that anxiety about your presentation...",
  "question": "What specifically about the presentation was most concerning?"
}
```

### Generate Title

```bash
POST /title
Content-Type: application/json

{
  "content": "Today was a difficult day at work..."
}
```

Response:
```json
{
  "title": "A Difficult Day at Work"
}
```

### Chat About Entry

```bash
POST /chat
Content-Type: application/json

{
  "entryContent": "I went for a walk and it helped clear my mind...",
  "message": "Why did walking help?",
  "history": [],
  "companion": {
    "name": "Yuzu",
    "avatar": "🐨",
    "traits": ["Wise", "Calm"]
  }
}
```

Response:
```json
{
  "message": {
    "role": "assistant",
    "content": "Walking helps by providing both physical movement and mental space..."
  }
}
```

## Testing

### Quick Test Script

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test reflection endpoint (requires jq for pretty printing)
curl -X POST http://localhost:8000/reflection \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Today I felt anxious about my presentation.",
    "companion": {
      "name": "Yuzu",
      "avatar": "🐨",
      "traits": ["Friendly", "Supportive"]
    }
  }' | jq
```

### Using Swagger UI

1. Start the server: `python -m app.main`
2. Open http://localhost:8000/docs
3. Click "Try it out" on any endpoint
4. Fill in the request body
5. Click "Execute"

## Development

### Project Structure

```
mvlt-ai-service/
├── app/
│   ├── __init__.py        # Package initialization
│   ├── main.py            # FastAPI app and endpoints
│   ├── models.py          # Pydantic request/response models
│   ├── claude.py          # Claude API client
│   ├── prompts.py         # Prompt service
│   └── templates/         # Prompt templates (optional)
├── .env                   # Environment variables (not in git)
├── .env.example           # Example environment file
├── .gitignore
├── requirements.txt       # Python dependencies
└── README.md
```

### Adding New Endpoints

1. Define request/response models in `app/models.py`
2. Add endpoint function in `app/main.py`
3. Implement any new services as needed

### Hot Reload

The server will automatically reload when you make changes to Python files (thanks to uvicorn's `--reload` flag, which can be added in `main.py`).

## Troubleshooting

### API Key Not Set

**Error**: `ValueError: ANTHROPIC_API_KEY not set`

**Solution**: Make sure you've created a `.env` file and added your API key:
```bash
cp .env.example .env
# Edit .env and add your API key
```

### Port Already in Use

**Error**: `Address already in use`

**Solution**: Either stop the other process using port 8000, or change the port in `app/main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Use different port
```

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**: Make sure you've activated the virtual environment and installed dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### CORS Errors from Flutter

The server is configured to allow all origins for local development. If you still see CORS errors:
1. Check that the server is running
2. Verify you're using the correct URL in Flutter (http://localhost:8000)
3. Check server logs for any errors

## Deployment to Render

This service is optimized for deployment to [Render](https://render.com) on their free tier.

### Prerequisites

1. **GitHub Repository**: Push your code to GitHub
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **Anthropic API Key**: Get your key from [console.anthropic.com](https://console.anthropic.com/)

### Deployment Steps

#### 1. Push to GitHub

```bash
# Add remote (if not already added)
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO.git

# Commit and push
git add .
git commit -m "Prepare for Render deployment"
git push -u origin main
```

#### 2. Create New Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select the `mvlt-ai-service` repository

#### 3. Configure the Service

**Basic Settings:**
- **Name**: `mvlt-ai-service` (or your preferred name)
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Instance Type:**
- Select **"Free"** tier

#### 4. Set Environment Variables

In the "Environment" section, add:

| Key | Value | Notes |
|-----|-------|-------|
| `ANTHROPIC_API_KEY` | `sk-ant-...` | **Required** - Your Claude API key |
| `CORS_ORIGINS` | `*` | Allow all origins (or specify your frontend URL) |
| `CLAUDE_MODEL` | `claude-sonnet-4-5` | Optional - defaults to this |
| `APP_DEBUG` | `false` | Disable debug mode in production |

**Important**: Keep `ANTHROPIC_API_KEY` secret - don't expose it in logs!

#### 5. Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies (~500MB for ML models)
   - Start the service
3. Wait 5-10 minutes for first deployment (downloading ML models)

#### 6. Verify Deployment

Once deployed, your service will be available at:
```
https://mvlt-ai-service.onrender.com
```

Test the health endpoint:
```bash
curl https://mvlt-ai-service.onrender.com/health
```

View API docs:
```
https://mvlt-ai-service.onrender.com/docs
```

### Render Configuration File

This repository includes a `render.yaml` file for automatic configuration. Render will detect and use this file automatically.

### Important Notes for Free Tier

**Cold Starts:**
- Free tier sleeps after 15 minutes of inactivity
- First request after sleep takes ~30-60 seconds (loads 500MB NER model)
- Subsequent requests are fast (<1 second)

**Memory Limit:**
- Free tier has 512MB RAM
- NER service uses ~500MB for Flair model
- If you hit memory limits, consider disabling the `/tags` endpoint

**Build Time:**
- Initial deploy: ~5-10 minutes (downloads PyTorch, Transformers, Flair)
- Rebuilds: ~3-5 minutes (cached dependencies)

**Bandwidth:**
- 100GB/month outbound bandwidth
- Sufficient for low-traffic production use

### Monitoring

1. **Logs**: View real-time logs in Render Dashboard
2. **Health Check**: Render automatically monitors `/health` endpoint
3. **Metrics**: Basic metrics available in dashboard

### Updating Your Deployment

Render automatically redeploys when you push to `main`:

```bash
git add .
git commit -m "Update API"
git push origin main
```

### Troubleshooting Deployment

**Build Fails:**
- Check that `requirements.txt` is present
- Verify Python version compatibility (uses 3.11 on Render)
- Check build logs for specific errors

**Service Won't Start:**
- Verify `ANTHROPIC_API_KEY` is set correctly
- Check start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Review logs for startup errors

**Memory Issues:**
- Free tier has 512MB RAM limit
- NER model uses ~500MB
- Consider disabling `/tags` endpoint if needed

**Slow First Request:**
- This is normal on free tier (cold start + model loading)
- Consider upgrading to paid tier ($7/month) for always-on service

### Alternative Deployment Options

If Render doesn't meet your needs, this service can also deploy to:

- **Fly.io**: Always-on free tier, requires Docker
- **Railway**: $5/month credit, excellent DX
- **Google Cloud Run**: Serverless, pay-per-use
- **Heroku**: Paid tiers only (no free tier)

See the included `Dockerfile` and `.dockerignore` for containerized deployments.

## Next Steps

After confirming the server works:

1. **Add Prompt Template**: Copy reflection template from Flutter app to `app/templates/reflection.yaml`
2. **Integrate with Flutter**: Use the external AI client in Flutter app
3. **Add Error Handling**: Improve error messages and handling
4. **Add Authentication**: Implement JWT validation when ready
5. **Monitor Usage**: Keep an eye on Anthropic API usage and costs

## License

Same as MVLT parent project.
