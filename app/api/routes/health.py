"""Health check endpoint."""
from fastapi import APIRouter
from app.dependencies import SettingsDep

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(settings: SettingsDep):
    """
    Health check endpoint to verify service is running.

    Returns:
        dict: Service status, name, and version
    """
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
    }
