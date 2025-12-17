# CLAUDE.md - MVLT AI Service Architecture Guide

A comprehensive guide to the FastAPI-based MVLT AI Service architecture. Use this to quickly understand design patterns, important architectural decisions, and development workflows.

## Quick Start for Claude Instances

To be immediately productive in this codebase:

1. **Port**: Local development runs on **8765**, production uses `$PORT` environment variable
2. **API Key**: Required `ANTHROPIC_API_KEY` environment variable
3. **Main Entry**: `app/main.py` - contains the application factory
4. **Services**: Three core services in `app/services/`:
   - `claude_service.py` - Claude API wrapper
   - `prompt_service.py` - Template-based prompt building
   - `ner_service.py` - Named Entity Recognition (uses Claude Haiku API)

---

## 1. Architecture Patterns & Design Decisions

### 1.1 Application Factory Pattern

**Location**: `app/main.py`

The application uses a traditional FastAPI app factory pattern:

```python
def create_app() -> FastAPI:
    """Application factory for creating FastAPI instance."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        description="AI service for MVLT journaling app",
        version=settings.app_version,
        debug=settings.app_debug,
    )
    # Configure middleware, exception handlers, routers
    return app

app = create_app()
```

**Benefits**:
- Decouples app configuration from instantiation
- Easy to test (create multiple app instances with different configs)
- Follows FastAPI best practices
- All configuration centralized in factory function

### 1.2 Dependency Injection System

**Location**: `app/dependencies.py`

FastAPI's built-in dependency injection with custom patterns for service instantiation:

#### Service Instantiation Pattern:

**Fresh Instance Pattern** (All services: ClaudeService, PromptService, NERService):
```python
def get_claude_service():
    from app.services.claude_service import ClaudeService
    settings = get_settings()
    return ClaudeService(settings)

def get_ner_service():
    from app.services.ner_service import NERService
    settings = get_settings()
    return NERService(settings)
```
- New instance created per request
- All services are lightweight and stateless
- Settings injected fresh each time
- No caching needed (Claude API handles model loading on their end)

#### Type Aliases for Clean Route Signatures:
```python
SettingsDep = Annotated[Settings, Depends(get_settings)]
ClaudeDep = Annotated[object, Depends(get_claude_service)]
PromptDep = Annotated[object, Depends(get_prompt_service)]
NERDep = Annotated[object, Depends(get_ner_service)]
```

**Usage in routes**:
```python
@router.post("/reflection")
async def generate_reflection(
    req: ReflectionRequest,
    claude: ClaudeDep,      # Fresh ClaudeService
    prompts: PromptDep,     # Fresh PromptService
):
    pass
```

**Design Decision**: Separate fresh vs singleton patterns based on:
- **Fresh**: Stateless, configuration-based services
- **Singleton**: Expensive initialization, stateful services

### 1.3 Middleware Stack

**Location**: `app/core/middleware.py`

Three custom middleware layers in execution order:

1. **RequestLoggingMiddleware**:
   - Logs all incoming requests with method, path, client IP
   - Measures request duration
   - Logs response status codes and timing
   - Catches and logs failed requests

2. **ErrorHandlingMiddleware**:
   - Catches unexpected exceptions
   - Logs full stack traces
   - Re-raises to allow exception handlers to process

3. **NoCacheMiddleware**:
   - Adds HTTP cache-control headers to all responses
   - Prevents browser/proxy caching of API responses
   - Headers: `no-cache, no-store, must-revalidate, max-age=0`

**Middleware order matters**:
- Registered LIFO (Last In First Out)
- CORS middleware added first (highest priority)
- Custom middleware in reverse order in code

### 1.4 Exception Handling System

**Location**: `app/core/exceptions.py`

Tiered exception handling strategy:

#### Custom Exception Classes:
```python
class AIServiceError(Exception):           # Base exception
class PromptBuildError(AIServiceError):    # Prompt building failures (500)
class ClaudeAPIError(AIServiceError):      # Claude API failures (502)
```

#### Exception Handler Registration (in order of specificity):
1. `AIServiceError` → Custom JSON response with message, status code, path
2. `APIError` (Anthropic) → 502 Bad Gateway
3. `APITimeoutError` → 504 Gateway Timeout
4. `RateLimitError` → 429 Too Many Requests
5. `RequestValidationError` (Pydantic) → 422 Unprocessable Entity + validation details
6. Generic `Exception` → 500 Internal Server Error

**Pattern**: All handlers return JSONResponse with consistent format:
```json
{
  "error": "ExceptionClassName",
  "message": "Human readable error",
  "details": "Optional validation errors",
  "path": "/endpoint"
}
```

### 1.5 Configuration Management

**Location**: `app/config.py`

Uses Pydantic's `BaseSettings` for environment variable management:

```python
class Settings(BaseSettings):
    # Application config
    app_name: str = "MVLT AI Service"
    app_version: str = "0.1.0"
    app_debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8765  # Local dev port
    
    # Claude API
    anthropic_api_key: str  # Required, no default
    claude_model: str = "claude-sonnet-4-5"
    claude_max_tokens: int = 1000
    claude_temperature: float = 0.7
    
    # Content limits
    max_entry_content_length: int = 10000
    max_chat_message_length: int = 5000
    max_title_content_length: int = 1500
    
    # CORS
    cors_origins: list[str] = ["*"]  # Restrict in production
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

def get_settings() -> Settings:
    return Settings()  # Fresh instance each call
```

**Key Design**:
- Environment variables override defaults via `.env` file
- No caching on `get_settings()` - fresh instance per call
- Validation happens at initialization (raises ValueError if ANTHROPIC_API_KEY missing)
- Case-insensitive for environment variables

---

## 2. Service Layer Architecture

### 2.1 Claude Service (API Wrapper)

**Location**: `app/services/claude_service.py`

Wraps the Anthropic Python SDK with sensible defaults:

```python
class ClaudeService:
    def __init__(self, settings: Settings):
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.claude_model
        self.max_tokens = settings.claude_max_tokens
        self.temperature = settings.claude_temperature
    
    async def chat(
        self,
        system_prompt: str,
        user_message: str | list,  # Single string or message dicts
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        """Call Claude API, return response text."""
```

**Important Details**:
- Uses `AsyncAnthropic` for async/await compatibility
- Converts single string messages to API format
- Supports full conversation history (list of {role, content} dicts)
- Returns only the text content from response

**Design Decision**: Fresh instance per request allows:
- Per-request configuration overrides
- No state pollution between requests
- Easy to test with mocked settings

### 2.2 Prompt Service (Template System)

**Location**: `app/services/prompt_service.py`

Builds system prompts from templates with variable substitution:

#### Template Loading:
```python
class PromptService:
    def __init__(self):
        self.templates_dir = Path(__file__).parent / "templates"
    
    def build_reflection_prompt(
        self,
        companion_name: str,
        traits: List[str],
        content: str
    ) -> str:
        template_path = self.templates_dir / "reflection.yaml"
        if template_path.exists():
            # Load YAML template
        else:
            # Use fallback default template
```

#### Available Prompt Builders:

1. **Reflection Prompt**:
   - Variables: `{{companion_name}}`, `{{companion_avatar}}`, `{{personality_descriptor}}`, `{{personality_instructions}}`, `{{user_entry}}`, `{{word_count}}`
   - Truncates content to 2000 chars
   - Expects JSON response format with "reflection" and "question" fields

2. **Chat Prompt**:
   - Variables: companion name, traits, entry content
   - Builds conversational system prompt with entry context
   - Encourages curious, supportive behavior

#### Personality System:
```python
def _build_personality(self, traits: List[str]) -> str:
    # Converts ["Friendly", "Supportive"] -> "friendly and supportive"

def _get_trait_behaviors(self, traits: List[str]) -> str:
    trait_map = {
        'Friendly': 'Be warm and approachable...',
        'Wise': 'Share thoughtful insights...',
        # ... 15+ personality traits
    }
```

**Design Decision**: 
- Template files are optional - fallback defaults in code
- Trait-to-behavior mapping centralized for consistency
- Truncation at service level prevents oversized prompts

### 2.3 NER Service (Named Entity Recognition)

**Location**: `app/services/ner_service.py`

Extracts named entities from text using Claude 3.5 Haiku API:

```python
class NERService:
    def __init__(self, settings: Settings):
        # Uses Claude API - no local model loading required
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.ner_model  # "claude-3-5-haiku-20241022"
        self.max_tokens = settings.ner_max_tokens  # 500
        self.temperature = settings.ner_temperature  # 0.3

    async def extract_tags(self, content: str) -> List[str]:
        system_prompt = """Extract named entities (people, places, organizations, dates, events).
        Return ONLY a JSON array of strings."""

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": content[:5000]}]
        )

        tags = json.loads(response.content[0].text.strip())
        # Deduplicate while preserving order
        return unique_tags
```

**Key Benefits Over Previous Flair Implementation**:
- **No memory overhead**: No 500MB model to load
- **Fits on free tier**: Render 512MB limit no longer an issue
- **No cold starts**: API-based, no model initialization delay
- **Better accuracy**: Claude understands context better than Flair
- **Cost-effective**: ~$0.11 per 1000 requests with Haiku
- **Fresh instance pattern**: Consistent with other services

**Cost Analysis**:
- Model: Claude 3.5 Haiku (cheapest Claude model)
- Input: ~$0.25 per 1M tokens
- Output: ~$1.25 per 1M tokens
- Average request: ~200 input tokens, ~50 output tokens
- **Cost per 1000 requests: ~$0.11**
- For low traffic (1000 req/month): practically free

**Configuration** (`app/config.py`):
- `ner_model`: "claude-3-5-haiku-20241022"
- `ner_max_tokens`: 500 (sufficient for tag lists)
- `ner_temperature`: 0.3 (lower for consistency)

---

## 3. API Routes & Endpoint Structure

### 3.1 Route Organization

**Location**: `app/api/routes/`

Each route in its own file with consistent pattern:

```python
# app/api/routes/{endpoint}.py
from fastapi import APIRouter

router = APIRouter(tags=["tag_name"])

@router.post("/endpoint")
async def endpoint_handler(req: RequestModel, dep: DepType):
    # Implementation
    return ResponseModel(...)
```

All routers exported and registered in `app/api/routes/__init__.py`:
```python
from app.api.routes.health import router as health_router
from app.api.routes.reflection import router as reflection_router
# ...

__all__ = [
    "health_router",
    "reflection_router",
    # ...
]
```

### 3.2 Request/Response Models

**Location**: `app/models/requests.py` and `app/models/responses.py`

All models use Pydantic `BaseModel` with Field validation:

#### Request Models:
```python
class CompanionSettings(BaseModel):
    name: str
    avatar: str
    traits: List[str]

class ReflectionRequest(BaseModel):
    content: str = Field(..., max_length=10000)
    companion: CompanionSettings

class ChatRequest(BaseModel):
    entryContent: str = Field(..., max_length=4000)
    message: str = Field(..., max_length=1000)
    history: List[ChatMessage] = Field(default_factory=list)
    companion: CompanionSettings
```

#### Response Models:
```python
class ReflectionResponse(BaseModel):
    reflection: str = Field(..., description="≤500 chars")
    question: str = Field(..., description="≤200 chars")

class ChatResponse(BaseModel):
    message: dict = Field(..., description="Assistant's response message")
```

**Validation Strategy**:
- Field length limits prevent oversized API calls
- Pattern matching for strict formats (e.g., `role: str = Field(..., pattern="^(user|assistant)$")`)
- Descriptions for API documentation

### 3.3 Endpoint Patterns

#### 1. Health Check (`/health`)
```python
@router.get("/health")
async def health_check(settings: SettingsDep):
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
    }
```
- No dependencies on external services
- Fast response for monitoring/load balancers
- Confirms service is alive

#### 2. Reflection Generation (`/reflection`)
```python
@router.post("/reflection", response_model=ReflectionResponse)
async def generate_reflection(
    req: ReflectionRequest,
    claude: ClaudeDep,
    prompts: PromptDep,
):
    system_prompt = prompts.build_reflection_prompt(
        companion_name=req.companion.name,
        traits=req.companion.traits,
        content=req.content
    )
    response = await claude.chat(system_prompt, req.content)
    clean_response = strip_markdown_json(response)
    result = json.loads(clean_response)
    return ReflectionResponse(...)
```

**Special Pattern**: `strip_markdown_json()` helper
- Claude often wraps JSON in markdown code fences despite instructions
- Regex strips `\`\`\`json ... \`\`\`` format
- Fallback handling if JSON parsing fails (returns truncated response + default question)

#### 3. Title Generation (`/title`)
```python
@router.post("/title", response_model=TitleResponse)
async def generate_title(req: TitleRequest, claude: ClaudeDep):
    prompt = "Generate a concise 5-10 word title..."
    response = await claude.chat(prompt, req.content[:1500])
    return TitleResponse(title=response.strip())
```

**Simplest pattern**: Direct prompt, no template service needed

#### 4. Chat (`/chat`)
```python
@router.post("/chat", response_model=ChatResponse)
async def chat_about_entry(
    req: ChatRequest,
    claude: ClaudeDep,
    prompts: PromptDep,
):
    system_prompt = prompts.build_chat_prompt(...)
    messages = [{"role": msg.role, "content": msg.content} for msg in req.history]
    messages.append({"role": "user", "content": req.message})
    response = await claude.chat(system_prompt, messages)
    return ChatResponse(message={"role": "assistant", "content": response})
```

**Conversation History Pattern**:
- Client sends full history in each request
- Server appends new message
- Claude processes full conversation
- Simple stateless design (server doesn't store conversation state)

#### 5. Tags Extraction (`/tags`)
```python
@router.post("/tags", response_model=TagsResponse)
async def generate_tags(ner: NERDep, req: TagsRequest = Body(...)):
    tags = await ner.extract_tags(req.content)
    return TagsResponse(tags=tags)
```

**Uses Claude 3.5 Haiku API** for cost-effective entity extraction (~$0.11 per 1000 requests)

---

## 4. Configuration & Environment

### 4.1 Environment Variables

**File**: `.env.example` (source of truth for required/optional variables)

#### Required Variables:
```
ANTHROPIC_API_KEY=sk-ant-...  # From https://console.anthropic.com/
```

#### Optional Variables with Defaults:
```
# App config
APP_NAME=MVLT AI Service
APP_VERSION=0.1.0
APP_DEBUG=false

# Server
HOST=0.0.0.0
PORT=8765  # Local dev, production uses $PORT environment variable

# Claude API
CLAUDE_MODEL=claude-sonnet-4-5
CLAUDE_MAX_TOKENS=1000
CLAUDE_TEMPERATURE=0.7

# Content limits
MAX_ENTRY_CONTENT_LENGTH=10000
MAX_CHAT_MESSAGE_LENGTH=5000
MAX_TITLE_CONTENT_LENGTH=1500

# CORS
CORS_ORIGINS=*  # Use ["https://myapp.com", "https://app.myapp.com"] in production
```

### 4.2 Port Configuration

**Local Development**: `8765` (hardcoded default in `app/config.py`)

**Production**: Uses `$PORT` environment variable
- Render sets this automatically based on free tier port assignment
- Start command in render.yaml: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 4.3 Makefile Commands

**File**: `Makefile` (minimal, 2 commands)

```makefile
run:
    @echo "Checking for processes on port 8765..."
    @lsof -ti:8765 | xargs kill -9 2>/dev/null || true
    @echo "Starting server..."
    source venv/bin/activate && python -m app.main

install:
    pip install -r requirements.txt
```

**Usage**:
```bash
make install  # Install dependencies
make run      # Kill any existing process on 8765, start server
```

---

## 5. Development Workflow

### 5.1 Local Development Setup

1. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   make install
   # Or: pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env, add ANTHROPIC_API_KEY
   ```

4. **Run server**:
   ```bash
   make run
   # Or: python -m app.main
   ```

5. **Access API documentation**:
   - Swagger UI: http://localhost:8765/docs
   - ReDoc: http://localhost:8765/redoc

### 5.2 Adding New Endpoints

1. **Create route file** in `app/api/routes/{endpoint}.py`:
   ```python
   from fastapi import APIRouter
   from app.models import RequestModel, ResponseModel
   from app.dependencies import SomeDep
   
   router = APIRouter(tags=["feature_name"])
   
   @router.post("/endpoint", response_model=ResponseModel)
   async def handler(req: RequestModel, dep: SomeDep):
       return ResponseModel(...)
   ```

2. **Add models** to `app/models/requests.py` and `app/models/responses.py`

3. **Export router** in `app/api/routes/__init__.py`

4. **Register router** in `app/main.py`:
   ```python
   from app.api.routes import new_router
   # ...
   app.include_router(new_router)
   ```

### 5.3 Adding New Services

1. **Create service file** in `app/services/{service}.py`:
   ```python
   class MyService:
       def __init__(self, ...):
           pass
       
       def method(self, ...):
           pass
   ```

2. **Export in** `app/services/__init__.py`

3. **Add dependency** in `app/dependencies.py`:
   ```python
   def get_my_service():
       from app.services.my_service import MyService
       return MyService()
   
   MyServiceDep = Annotated[object, Depends(get_my_service)]
   ```

4. **Use in routes**:
   ```python
   async def handler(my_service: MyServiceDep):
       pass
   ```

---

## 6. Important Gotchas & Performance Considerations

### 6.1 NER via Claude API

**Implementation**: Uses Claude 3.5 Haiku API instead of local Flair model.

**Benefits**:
- No memory overhead (API-based, not local model)
- No model loading delays
- Fits comfortably on Render free tier (512MB)
- Cost: ~$0.11 per 1000 requests
- Better entity recognition (Claude understands context)

**Trade-offs**:
- API latency (~1-2 seconds per request vs <1 second with cached Flair)
- Requires internet connection
- Small cost per request (though minimal for low traffic)
- Dependent on Anthropic API availability

**Current Status**: Optimized for free tier deployment. No memory constraints.

### 6.2 Cold Start Performance

On Render free tier (which sleeps after 15 minutes):

**First request after sleep**:
- Service wake-up: ~10-15 seconds
- Model download/initialization: If not cached, ~5-10 seconds
- First request processing: ~5-10 seconds
- **Total**: ~30-60 seconds (acceptable but noticeable)

**Subsequent requests**: <1 second (model cached in memory)

**User Impact**: Long delays on first request, then fast. Consider communicating this to users.

### 6.3 CORS Configuration

**Current Setting**: `cors_origins: ["*"]` - allows all origins

**Security Implications**:
- Any domain can call your API
- Any frontend can access your endpoints
- Acceptable for internal/development but risky for production

**Production Recommendation**:
```yaml
CORS_ORIGINS=https://myapp.com,https://app.myapp.com
```

### 6.4 Claude API Response Handling

**JSON Parsing Issue**: Claude often returns JSON wrapped in markdown code fences:
```
Response: ```json
{"reflection": "...", "question": "..."}
```
```

**Solution**: `strip_markdown_json()` in reflection.py
- Regex pattern: `^```(?:json)?\s*\n?(.*?)\n?```$`
- Strips markdown, leaves clean JSON
- Has fallback: if parsing fails, returns truncated response + default question

**Why This Matters**: Claude is less consistent with following "return only JSON" instructions than some models.

### 6.5 Async/Await Usage

**All API handlers are async**:
```python
async def generate_reflection(...):
```

**Why**: 
- Claude SDK uses `AsyncAnthropic` for async support
- FastAPI runs async handlers concurrently
- Allows multiple simultaneous requests without blocking

**Important**: Never use blocking operations in handlers (e.g., `time.sleep()`, synchronous file I/O, synchronous HTTP calls). Use async alternatives.

### 6.6 Content Truncation

Multiple truncation points prevent oversized requests:

1. **Request model validation**: `Field(..., max_length=10000)`
2. **Service-level truncation**:
   ```python
   prompt = prompt.replace("{{user_entry}}", content[:2000])
   ```
3. **Controller-level truncation**:
   ```python
   response = await claude.chat(prompt, req.content[:1500])
   ```

**Reason**: Prevents accidentally sending massive content to Claude API (costs money, slower responses).

### 6.7 Dependency Injection Gotchas

**All Services Use Fresh Instances**:
```python
def get_claude_service():
    settings = get_settings()  # Fresh settings each call
    return ClaudeService(settings)

def get_ner_service():
    settings = get_settings()  # Fresh settings each call
    return NERService(settings)
```

**Critical**: Settings is NOT singleton - each route handler gets fresh settings. All services (Claude, Prompt, NER) are instantiated fresh per request for consistency and statelessness.

---

## 7. Deployment to Render

### 7.1 Render Configuration

**File**: `render.yaml` (auto-detected by Render)

Key settings:
```yaml
startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
healthCheckPath: /health
plan: free
```

### 7.2 Deployment Steps

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Deploy to Render"
   git push origin main
   ```

2. **Create web service on Render dashboard**

3. **Set environment variables**:
   - `ANTHROPIC_API_KEY` (manually - don't expose in config)
   - `CORS_ORIGINS=*` (or restrict to frontend URL)

4. **Deploy** - Render automatically:
   - Clones repo
   - Installs dependencies (lightweight - no ML models)
   - Starts service

### 7.3 Important Deployment Notes

**Build time**: 2-3 minutes (lightweight Python dependencies only)

**Memory**: 512MB free tier is sufficient (no local ML models)

**Bandwidth**: 100GB/month outbound

**Monitoring**: Render checks `/health` endpoint for service status

---

## 8. Code Style & Patterns

### 8.1 Logging

Located in `app/core/middleware.py`:

```python
import logging

logger = logging.getLogger("mvlt-ai-service")
logger.info("User message")
logger.error("Error message")
logger.exception("Full traceback")
```

**Output format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

### 8.2 Error Messages

Structured error responses with context:

```python
async def ai_service_exception_handler(request: Request, exc: AIServiceError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "path": str(request.url.path),
        }
    )
```

### 8.3 Type Hints

Consistent use of Python type hints:

```python
def method(self, text: str, count: int = 5) -> List[str]:
    pass

async def handler(
    req: RequestModel,
    service: ServiceDep,
) -> ResponseModel:
    pass
```

---

## 9. Testing Endpoints Locally

### Using curl:

```bash
# Health check
curl http://localhost:8765/health

# Reflection generation
curl -X POST http://localhost:8765/reflection \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Today I felt anxious...",
    "companion": {
      "name": "Yuzu",
      "avatar": "🐨",
      "traits": ["Friendly", "Supportive"]
    }
  }'

# Title generation
curl -X POST http://localhost:8765/title \
  -H "Content-Type: application/json" \
  -d '{"content": "Today was difficult..."}'

# Tags extraction
curl -X POST http://localhost:8765/tags \
  -H "Content-Type: application/json" \
  -d '{"content": "I met with Sarah and John about the project..."}'
```

### Using Swagger UI:

1. Open http://localhost:8765/docs
2. Click "Try it out" on any endpoint
3. Fill request body
4. Click "Execute"
5. See response and curl command

---

## 10. Project Dependencies

**File**: `requirements.txt`

Key dependencies:

```
fastapi==0.109.0              # Web framework
uvicorn[standard]==0.27.0     # ASGI server
anthropic==0.39.0             # Claude API SDK
pydantic-settings==2.1.0      # Config management
pyyaml==6.0.1                 # Template parsing
```

**Lightweight build**: All ML operations handled via Claude API, no local models required.

---

## 11. Directory Structure

```
mvlt-ai-service/
├── app/                          # Application package
│   ├── __init__.py
│   ├── main.py                   # App factory, middleware, exception handlers, router registration
│   ├── config.py                 # Pydantic Settings, environment variable loading
│   ├── dependencies.py           # Dependency injection: services and type aliases
│   │
│   ├── core/                     # Core infrastructure
│   │   ├── __init__.py
│   │   ├── exceptions.py         # Exception classes and handlers
│   │   └── middleware.py         # Request logging, error handling, cache control
│   │
│   ├── api/                      # API endpoints
│   │   ├── __init__.py
│   │   └── routes/               # Endpoint route files
│   │       ├── __init__.py
│   │       ├── health.py         # GET /health
│   │       ├── reflection.py     # POST /reflection
│   │       ├── title.py          # POST /title
│   │       ├── chat.py           # POST /chat
│   │       └── tags.py           # POST /tags
│   │
│   ├── services/                 # Business logic / external integrations
│   │   ├── __init__.py
│   │   ├── claude_service.py     # Claude API wrapper
│   │   ├── prompt_service.py     # Prompt building from templates
│   │   └── ner_service.py        # Named entity recognition (singleton)
│   │
│   └── models/                   # Pydantic request/response models
│       ├── __init__.py
│       ├── requests.py           # Request models (ReflectionRequest, etc.)
│       └── responses.py          # Response models (ReflectionResponse, etc.)
│
├── .env                          # Environment variables (not in git)
├── .env.example                  # Template for .env
├── .gitignore
├── .dockerignore
├── requirements.txt              # Python dependencies
├── Makefile                      # Development commands
├── render.yaml                   # Render deployment configuration
├── README.md                     # User documentation
└── CLAUDE.md                     # This file
```

---

## 12. Common Tasks

### Task: Fix a Bug in Reflection Endpoint

1. Check logs: Look at RequestLoggingMiddleware output in console
2. Find route: `app/api/routes/reflection.py` - `generate_reflection()` function
3. Add debugging:
   ```python
   logger.error(f"Prompt built: {system_prompt[:100]}...")
   logger.error(f"Raw response: {response[:200]}...")
   ```
4. Test locally with curl or Swagger UI
5. Fix issue
6. Push to GitHub (auto-redeploys on Render)

### Task: Add New Personality Trait

1. Edit `app/services/prompt_service.py`
2. Add to `_get_trait_behaviors()` dict:
   ```python
   'Mystical': 'Embrace curiosity about the unknown...',
   ```
3. Test with curl:
   ```bash
   curl -X POST http://localhost:8765/reflection \
     -d '{"companion": {"traits": ["Mystical"]}}'
   ```

### Task: Increase Claude Max Tokens

1. Edit `app/config.py`: `claude_max_tokens: int = 2000`
2. Or set environment variable: `CLAUDE_MAX_TOKENS=2000`
3. Restart server or environment changes will apply on next request

### Task: Change Port for Production

- Render uses `$PORT` environment variable automatically
- Local development hardcoded to 8765 in `config.py`
- To change local: `PORT=9000 python -m app.main`

---

## 13. Debugging Tips

### Enable Debug Mode

In `.env`:
```
APP_DEBUG=true
```

- Enables uvicorn reload on file changes
- More verbose error messages
- Better for development

### Check Logs

Routes log via middleware:
```
2024-12-17 13:27:15,123 - mvlt-ai-service - INFO - Incoming request: POST /reflection from 127.0.0.1
2024-12-17 13:27:18,456 - mvlt-ai-service - INFO - Response: POST /reflection status=200 duration=3.333s
```

### Test with API Documentation

- Swagger UI automatically generated at `/docs`
- Every endpoint has "Try it out" button
- Shows exact curl command used
- Displays response status and body

### Check NER Service

NER service initializes per request:
```
INFO - NER service initialized with model: claude-3-5-haiku-20241022
INFO - Extracted 5 unique tags from content
```

No model loading delays - Claude API handles all processing.

---

## 14. Production Checklist

Before deploying to production:

- [ ] Set `APP_DEBUG=false`
- [ ] Restrict `CORS_ORIGINS` to your frontend domain
- [ ] Verify `ANTHROPIC_API_KEY` is set in Render environment
- [ ] Test `/health` endpoint after deployment
- [ ] Monitor Anthropic API usage for cost overruns
- [ ] Set up log monitoring/alerting if available
- [ ] Document any API changes to frontend team
- [ ] Test endpoints from production URL (not localhost)

---

## 15. Useful References

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Anthropic API**: https://docs.anthropic.com/
- **Claude Models**: https://docs.anthropic.com/en/docs/models-overview
- **Pydantic**: https://docs.pydantic.dev/
- **Render Docs**: https://render.com/docs

---

## Summary

This FastAPI service follows clean architecture principles:

- **Clear separation of concerns**: Routes, services, models, config
- **Dependency injection**: Services easily swappable for testing
- **Exception handling**: Comprehensive, typed exception handlers
- **Performance optimization**: Singleton NER service, content truncation
- **Type safety**: Python type hints throughout
- **Environment configuration**: Pydantic settings management
- **Logging & monitoring**: Request/response logging middleware

The architecture scales well for adding new endpoints, services, and features. All patterns are documented here for future Claude instances to understand immediately.

