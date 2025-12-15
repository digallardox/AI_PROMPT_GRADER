"""Custom exceptions and exception handlers."""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from anthropic import APIError, APITimeoutError, RateLimitError


class AIServiceError(Exception):
    """Base exception for AI service errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class PromptBuildError(AIServiceError):
    """Exception raised when prompt building fails."""
    def __init__(self, message: str = "Failed to build prompt"):
        super().__init__(message, status_code=500)


class ClaudeAPIError(AIServiceError):
    """Exception raised when Claude API call fails."""
    def __init__(self, message: str = "Claude API error"):
        super().__init__(message, status_code=502)


async def ai_service_exception_handler(request: Request, exc: AIServiceError):
    """Handle custom AI service exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "path": str(request.url.path),
        }
    )


async def anthropic_api_error_handler(request: Request, exc: APIError):
    """Handle Anthropic API errors."""
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={
            "error": "ClaudeAPIError",
            "message": f"Claude API error: {str(exc)}",
            "path": str(request.url.path),
        }
    )


async def anthropic_timeout_handler(request: Request, exc: APITimeoutError):
    """Handle Anthropic API timeout errors."""
    return JSONResponse(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        content={
            "error": "ClaudeTimeoutError",
            "message": "Claude API request timed out",
            "path": str(request.url.path),
        }
    )


async def anthropic_rate_limit_handler(request: Request, exc: RateLimitError):
    """Handle Anthropic API rate limit errors."""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "ClaudeRateLimitError",
            "message": "Claude API rate limit exceeded",
            "path": str(request.url.path),
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Invalid request data",
            "details": exc.errors(),
            "path": str(request.url.path),
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "path": str(request.url.path),
        }
    )
