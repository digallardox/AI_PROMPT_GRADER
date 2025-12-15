# FastAPI Architecture - Best Practices Structure

## Directory Structure

```
mvlt-ai-service/
├── app/
│   ├── main.py                    # Application factory (96 lines)
│   ├── config.py                  # Centralized settings (49 lines)
│   ├── dependencies.py            # Dependency injection (47 lines)
│   │
│   ├── api/                       # API layer
│   │   └── routes/                # Individual route files
│   │       ├── health.py          # GET /health
│   │       ├── reflection.py      # POST /reflection
│   │       ├── title.py           # POST /title
│   │       └── chat.py            # POST /chat
│   │
│   ├── models/                    # Data models
│   │   ├── requests.py            # Request validation models
│   │   └── responses.py           # Response models
│   │
│   ├── services/                  # Business logic layer
│   │   ├── claude_service.py      # Claude API integration
│   │   └── prompt_service.py      # Prompt building logic
│   │
│   ├── core/                      # Core utilities
│   │   ├── exceptions.py          # Custom exceptions + handlers
│   │   └── middleware.py          # Request logging + error handling
│   │
│   └── templates/                 # Prompt templates (YAML)
│
├── tests/                         # Unit and integration tests
├── requirements.txt               # Python dependencies
├── .env                           # Environment variables (git ignored)
├── .env.example                   # Example environment file
├── Makefile                       # Quick commands (make run)
└── README.md                      # Documentation
```

## Architecture Principles

### 1. Layered Architecture
- **API Layer** (`api/routes/`): HTTP concerns only (request/response)
- **Service Layer** (`services/`): Business logic and external API calls
- **Model Layer** (`models/`): Data validation and serialization
- **Core Layer** (`core/`): Cross-cutting concerns (exceptions, middleware)

### 2. Dependency Injection
Services are injected via FastAPI's `Depends()` system:
```python
@router.post("/reflection")
async def generate_reflection(
    req: ReflectionRequest,
    claude: ClaudeDep,        # Injected
    prompts: PromptDep,       # Injected
):
    ...
```

Benefits:
- Easy to mock for testing
- Lazy initialization (Claude client only created when needed)
- Singleton pattern for expensive resources

### 3. Configuration Management
All settings centralized in `config.py` using Pydantic BaseSettings:
```python
class Settings(BaseSettings):
    anthropic_api_key: str
    claude_model: str = "claude-sonnet-4-5"
    claude_max_tokens: int = 1000
    ...
```

Environment variables automatically loaded from `.env` file.

### 4. Error Handling
Custom exception handlers registered in `main.py`:
- `AIServiceError`: Base exception for service errors
- `ClaudeAPIError`: Claude API specific errors
- `PromptBuildError`: Prompt building failures
- Anthropic SDK errors (timeout, rate limit, API errors)

All exceptions return consistent JSON error responses.

### 5. Logging & Monitoring
Custom middleware logs all requests:
```
2025-12-11 13:28:19,651 - INFO - Incoming request: POST /title from 127.0.0.1
2025-12-11 13:28:41,051 - INFO - Response: POST /title status=200 duration=2.996s
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/reflection` | POST | Generate empathetic reflection + follow-up question |
| `/title` | POST | Generate journal entry title |
| `/chat` | POST | Chat conversation about journal entry |

## Adding New Endpoints

1. Create route file: `app/api/routes/new_feature.py`
```python
from fastapi import APIRouter
from app.models import NewRequest, NewResponse
from app.dependencies import ClaudeDep

router = APIRouter(tags=["new_feature"])

@router.post("/new-feature", response_model=NewResponse)
async def new_feature(req: NewRequest, claude: ClaudeDep):
    # Implementation
    ...
```

2. Export router: `app/api/routes/__init__.py`
```python
from app.api.routes.new_feature import router as new_feature_router
```

3. Include router: `app/main.py`
```python
app.include_router(new_feature_router)
```

Done! Zero impact on existing code.

## Testing

Services are easily testable due to dependency injection:
```python
# Mock Claude service for testing
mock_claude = MockClaudeService()
response = await generate_title(
    req=TitleRequest(content="Test"),
    claude=mock_claude  # Inject mock
)
```

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
make run
# or
python -m uvicorn app.main:app --port 8001 --reload

# Test endpoints
curl http://localhost:8001/health
```

## Production Considerations

### Environment Variables
Required in production:
- `ANTHROPIC_API_KEY`: Claude API key
- `CORS_ORIGINS`: Restrict to your domains (not "*")

Optional configuration:
- `APP_DEBUG=false`: Disable debug mode
- `CLAUDE_MAX_TOKENS=1000`: Adjust response length
- `CLAUDE_TEMPERATURE=0.7`: Adjust creativity

### Security
- CORS restricted to specific origins
- API key validation on startup
- Request validation via Pydantic
- Exception handlers prevent information leakage

### Monitoring
- All requests logged with duration
- Error tracking via exception handlers
- Health check endpoint for uptime monitoring

## Design Patterns Used

1. **Repository Pattern**: Services encapsulate external API access
2. **Dependency Injection**: FastAPI's `Depends()` system
3. **Factory Pattern**: `create_app()` application factory
4. **Singleton Pattern**: Lazy-initialized services
5. **Strategy Pattern**: Swappable AI providers (future)

## File Organization Rules

- One route per file (by feature/endpoint)
- One model type per file (requests vs responses)
- One service per file (by external dependency)
- Shared utilities in `core/`
- All exports through `__init__.py` files

## Benefits Over Previous Structure

| Aspect | Before | After |
|--------|--------|-------|
| **main.py** | 133 lines, all logic | 96 lines, just wiring |
| **Routes** | All in one file | 4 separate files |
| **Models** | One 53-line file | Split into requests/responses |
| **Services** | Global variables | Dependency injection |
| **Config** | Hardcoded values | Centralized settings |
| **Error Handling** | Try/catch blocks | Custom exception handlers |
| **Logging** | Print statements | Structured middleware logging |
| **Testing** | Difficult to mock | Easy dependency injection |
| **Adding Features** | Modify main.py | Add one file |
| **Team Collaboration** | Merge conflicts | Independent files |

## Code Metrics

- **Total Files**: 19 Python files
- **Total Lines**: ~744 lines (excluding tests)
- **Average File Size**: 39 lines
- **Largest File**: `prompt_service.py` (131 lines)
- **Smallest File**: Package `__init__.py` files (1-33 lines)

Clean, modular, and maintainable! 🎯
