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

## Next Steps

After confirming the server works:

1. **Add Prompt Template**: Copy reflection template from Flutter app to `app/templates/reflection.yaml`
2. **Integrate with Flutter**: Use the external AI client in Flutter app
3. **Add Error Handling**: Improve error messages and handling
4. **Add Authentication**: Implement JWT validation when ready to deploy
5. **Deploy**: Deploy to a hosting service (Railway, Fly.io, etc.)

## License

Same as MVLT parent project.
