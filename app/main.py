import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from anthropic import APIError, APITimeoutError, RateLimitError

# Import configuration
from app.config import get_settings

# Import routers
from app.routes import (
    health_router,
    reflection_router,
    title_router,
    chat_router,
    tags_router,
    refine_router,
)

# Import exception handlers
from app.core.exceptions import (
    AIServiceError,
    ai_service_exception_handler,
    anthropic_api_error_handler,
    anthropic_timeout_handler,
    anthropic_rate_limit_handler,
    validation_exception_handler,
    generic_exception_handler,
)

# Import middleware
from app.core.middleware import (
    RequestLoggingMiddleware,
    ErrorHandlingMiddleware,
    NoCacheMiddleware,
)


# Get settings (cached via lru_cache)
settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI service for MVLT journaling app - reflection, title generation, and chat",
    version=settings.app_version,
    debug=settings.app_debug,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Add custom middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(NoCacheMiddleware)

# Register exception handlers
app.add_exception_handler(AIServiceError, ai_service_exception_handler)
app.add_exception_handler(APIError, anthropic_api_error_handler)
app.add_exception_handler(APITimeoutError, anthropic_timeout_handler)
app.add_exception_handler(RateLimitError, anthropic_rate_limit_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
app.include_router(health_router)
app.include_router(reflection_router)
app.include_router(title_router)
app.include_router(chat_router)
app.include_router(tags_router)
app.include_router(refine_router)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.app_debug,
        log_level="info",
    )
