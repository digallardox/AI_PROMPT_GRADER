"""Dependency injection for FastAPI routes."""
from typing import Annotated
from fastapi import Depends

from app.config import Settings, get_settings


# Global service instances (lazy initialization)
_claude_client = None
_prompt_service = None
_ner_service = None


def get_claude_service():
    """
    Get or create Claude service instance (lazy initialization).

    Returns:
        ClaudeService: Singleton instance of Claude service
    """
    global _claude_client
    if _claude_client is None:
        # Import here to avoid circular dependencies
        from app.services.claude_service import ClaudeService
        settings = get_settings()
        _claude_client = ClaudeService(settings)
    return _claude_client


def get_prompt_service():
    """
    Get or create Prompt service instance (lazy initialization).

    Returns:
        PromptService: Singleton instance of prompt service
    """
    global _prompt_service
    if _prompt_service is None:
        # Import here to avoid circular dependencies
        from app.services.prompt_service import PromptService
        _prompt_service = PromptService()
    return _prompt_service


def get_ner_service():
    """
    Get or create NER service instance (lazy initialization).

    Returns:
        NERService: Singleton instance of NER service
    """
    global _ner_service
    if _ner_service is None:
        # Import here to avoid circular dependencies
        from app.services.ner_service import NERService
        _ner_service = NERService()
    return _ner_service


# Type aliases for cleaner route signatures
SettingsDep = Annotated[Settings, Depends(get_settings)]
ClaudeDep = Annotated[object, Depends(get_claude_service)]
PromptDep = Annotated[object, Depends(get_prompt_service)]
NERDep = Annotated[object, Depends(get_ner_service)]
