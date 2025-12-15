"""API routes package - exports all route routers."""
from app.api.routes.health import router as health_router
from app.api.routes.reflection import router as reflection_router
from app.api.routes.title import router as title_router
from app.api.routes.chat import router as chat_router
from app.api.routes.tags import router as tags_router

__all__ = [
    "health_router",
    "reflection_router",
    "title_router",
    "chat_router",
    "tags_router",
]
