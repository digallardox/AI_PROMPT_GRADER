"""Dependency injection for FastAPI routes."""
from typing import Annotated, Optional
from fastapi import Depends

from app.config import Settings, get_settings

# Global cache for singleton instances
_ner_service_instance: Optional[object] = None


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
    from app.services.prompt_service import PromptService
    return PromptService()


def get_ner_service():
    """
    Get or create a singleton NER service instance.

    The Flair NER model (~500MB) is loaded once at first request and cached
    for all subsequent requests. This significantly improves performance:
    - First request: ~10-15 seconds (model loads)
    - Subsequent requests: <1 second (model already in memory)

    Returns:
        NERService: Singleton instance of NER service
    """
    global _ner_service_instance

    if _ner_service_instance is None:
        # Import here to avoid circular dependencies
        from app.services.ner_service import NERService
        _ner_service_instance = NERService()

    return _ner_service_instance


# Type aliases for cleaner route signatures
SettingsDep = Annotated[Settings, Depends(get_settings)]
ClaudeDep = Annotated[object, Depends(get_claude_service)]
PromptDep = Annotated[object, Depends(get_prompt_service)]
NERDep = Annotated[object, Depends(get_ner_service)]
