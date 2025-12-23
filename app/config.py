"""Application configuration using Pydantic BaseSettings."""
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    app_name: str = "MVLT AI Service"
    app_version: str = "0.1.0"
    app_debug: bool = False

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8765

    # Claude API Configuration
    anthropic_api_key: str
    claude_model: str = "claude-sonnet-4-5"
    claude_max_tokens: int = 1000
    claude_temperature: float = 0.7

    # NER (Named Entity Recognition) Configuration
    ner_model: str = "claude-3-5-haiku-20241022"  # Cheaper, faster model for tag extraction
    ner_max_tokens: int = 500  # Tags don't need many tokens
    ner_temperature: float = 0.3  # Lower temperature for more consistent results

    # Content Limits
    max_entry_content_length: int = 10000
    max_chat_message_length: int = 5000
    max_title_content_length: int = 1500

    # Prompt Truncation
    reflection_content_truncate: int = 2000
    chat_content_truncate: int = 2000

    # CORS Configuration
    cors_origins: list[str] = ["*"]  # Restrict in production
    cors_credentials: bool = True
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings singleton.

    Settings are cached using lru_cache to avoid recreating the Settings object
    on every request. This follows FastAPI best practices since environment
    variables don't change during the application lifecycle.
    """
    return Settings()
