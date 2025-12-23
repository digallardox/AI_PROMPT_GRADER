"""API routes package - exports all route routers."""
from app.routes.health import router as health_router
from app.routes.reflection import router as reflection_router
from app.routes.title import router as title_router
from app.routes.chat import router as chat_router
from app.routes.tags import router as tags_router

__all__ = [
    "health_router",
    "reflection_router",
    "title_router",
    "chat_router",
    "tags_router",
]
