"""Custom middleware for request logging and processing."""
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mvlt-ai-service")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all incoming requests and responses."""

    async def dispatch(self, request: Request, call_next):
        """
        Log request details and timing.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/route handler

        Returns:
            Response from the route handler
        """
        # Start timer
        start_time = time.time()

        # Log request
        logger.info(
            f"Incoming request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log response
            logger.info(
                f"Response: {request.method} {request.url.path} "
                f"status={response.status_code} duration={duration:.3f}s"
            )

            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"error={str(e)} duration={duration:.3f}s"
            )
            raise


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware to catch and log unexpected errors."""

    async def dispatch(self, request: Request, call_next):
        """
        Catch and log unexpected errors.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/route handler

        Returns:
            Response from the route handler or error response
        """
        try:
            return await call_next(request)
        except Exception as e:
            logger.exception(f"Unhandled exception: {str(e)}")
            # Re-raise to let exception handlers deal with it
            raise


class NoCacheMiddleware(BaseHTTPMiddleware):
    """Middleware to add no-cache headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        """
        Add cache-control headers to prevent caching.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/route handler

        Returns:
            Response with no-cache headers
        """
        response = await call_next(request)

        # Add headers to prevent all forms of caching
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        return response
