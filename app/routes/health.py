from fastapi import APIRouter
from app.dependencies import SettingsDep

router = APIRouter(tags=["health"])


@router.get("/health")
@router.head("/health")
async def health_check(settings: SettingsDep):
    """
    Health check endpoint to verify service is running.
    Supports both GET and HEAD requests for uptime monitoring.

    Returns:
        dict: Service status, name, and version
    """
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
    }
