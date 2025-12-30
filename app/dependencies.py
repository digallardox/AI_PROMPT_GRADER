"""Dependency injection for FastAPI routes."""
from typing import Annotated
from fastapi import Depends

from app.config import Settings, get_settings


def get_claude_service():
    """
    Create a fresh Claude service instance (no caching).

    Returns:
        ClaudeService: New instance of Claude service
    """
    # Import here to avoid circular dependencies
    from app.services.claude_service import ClaudeService
    settings = get_settings()
    return ClaudeService(settings)


def get_prompt_service():
    """
    Create a fresh Prompt service instance (no caching).

    Returns:
        PromptService: New instance of prompt service
    """
    # Import here to avoid circular dependencies
    from app.services.prompts import PromptService
    return PromptService()


def get_ner_service():
    """
    Create a fresh NER service instance (no caching).

    Uses Claude API for entity extraction - no heavy model loading required.
    Each request creates a new instance with fresh settings.

    Returns:
        NERService: New instance of NER service
    """
    # Import here to avoid circular dependencies
    from app.services.ner_service import NERService
    settings = get_settings()
    return NERService(settings)


def get_refiner_service():
    """
    Create a fresh Refiner service instance (no caching).

    Uses Claude Haiku for cost-effective message refinement.
    Each request creates a new instance with fresh settings.

    Returns:
        RefinerService: New instance of refiner service
    """
    # Import here to avoid circular dependencies
    from app.services.refiner_service import RefinerService
    settings = get_settings()
    return RefinerService(settings)


# Type aliases for cleaner route signatures
SettingsDep = Annotated[Settings, Depends(get_settings)]
ClaudeDep = Annotated[object, Depends(get_claude_service)]
PromptDep = Annotated[object, Depends(get_prompt_service)]
NERDep = Annotated[object, Depends(get_ner_service)]
RefinerDep = Annotated[object, Depends(get_refiner_service)]
