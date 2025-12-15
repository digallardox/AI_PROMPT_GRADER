"""Claude API client service for AI operations."""
from anthropic import AsyncAnthropic
from app.config import Settings


class ClaudeService:
    """Service for interacting with Claude API."""

    def __init__(self, settings: Settings):
        """
        Initialize Claude service with settings.

        Args:
            settings: Application settings containing API key and model config

        Raises:
            ValueError: If ANTHROPIC_API_KEY is not set
        """
        if not settings.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not set. Please set it in .env file or environment."
            )

        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.claude_model
        self.max_tokens = settings.claude_max_tokens
        self.temperature = settings.claude_temperature

    async def chat(
        self,
        system_prompt: str,
        user_message: str | list,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        """
        Call Claude API with a system prompt and user message(s).

        Args:
            system_prompt: The system prompt to set context
            user_message: Either a single string or a list of message dicts
                         for conversation history
            max_tokens: Optional max tokens override (uses config default if not specified)
            temperature: Optional temperature override (uses config default if not specified)

        Returns:
            Claude's text response
        """
        # Convert single string to message format
        if isinstance(user_message, str):
            messages = [{"role": "user", "content": user_message}]
        else:
            messages = user_message

        # Call Claude API
        response = await self.client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=messages,
            max_tokens=max_tokens or self.max_tokens,
            temperature=temperature or self.temperature,
        )

        return response.content[0].text
