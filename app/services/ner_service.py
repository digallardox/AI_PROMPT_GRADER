"""NER (Named Entity Recognition) service for tag extraction using Claude API."""
import json
import logging
from pathlib import Path
from typing import List
from anthropic import AsyncAnthropic

from app.config import Settings

logger = logging.getLogger(__name__)


class NERService:
    """Service for extracting named entities/tags from text using Claude API."""

    def __init__(self, settings: Settings):
        """
        Initialize NER service with Claude API client.

        Uses Claude 3.5 Haiku for cost-effective, fast entity extraction.
        No model loading required - API-based service.

        Args:
            settings: Application settings containing API key and NER config

        Raises:
            ValueError: If ANTHROPIC_API_KEY is not set
        """
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")

        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.ner_model
        self.max_tokens = settings.ner_max_tokens
        self.temperature = settings.ner_temperature
        self.templates_dir = Path(__file__).parent / "prompts" / "templates"

        logger.info(f"NER service initialized with model: {self.model}")

    def _load_prompt(self) -> str:
        prompt_path = self.templates_dir / "ner.md"
        if prompt_path.exists():
            return prompt_path.read_text()

        # Fallback to default prompt
        return """You are a named entity recognition assistant. Extract all named entities from the user's journal entry, including:
- People (names)
- Places (cities, countries, locations)
- Organizations (companies, institutions)
- Dates and times (specific dates, events)
- Significant events or activities

Return ONLY a JSON array of entity strings. No duplicates. No explanation. Just the array.

Example format: ["John Smith", "New York", "2024", "Coffee Shop"]"""

    async def extract_tags(self, content: str) -> List[str]:
        """
        Extract named entities from text content using Claude API.

        Args:
            content: Text content to extract entities from

        Returns:
            List of extracted entity strings (deduplicated)

        Raises:
            Exception: If Claude API call or JSON parsing fails
        """
        try:
            # Load prompt from template
            system_prompt = self._load_prompt()

            # Call Claude API
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": content[:5000]  # Truncate long entries
                    }
                ]
            )

            # Extract response text
            response_text = response.content[0].text.strip()

            # Parse JSON response
            try:
                tags = json.loads(response_text)
            except json.JSONDecodeError:
                # Claude sometimes wraps in markdown - try to extract JSON
                logger.warning(f"Failed to parse JSON directly, attempting to clean: {response_text[:100]}")

                # Try to find JSON array in response
                import re
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    tags = json.loads(json_match.group())
                else:
                    logger.error(f"Could not extract JSON from response: {response_text}")
                    return []

            # Ensure it's a list
            if not isinstance(tags, list):
                logger.error(f"Response is not a list: {type(tags)}")
                return []

            # Remove duplicates while preserving order
            seen = set()
            unique_tags = []
            for tag in tags:
                # Convert to string and clean
                tag_str = str(tag).strip()
                if tag_str and tag_str not in seen:
                    seen.add(tag_str)
                    unique_tags.append(tag_str)

            logger.info(f"Extracted {len(unique_tags)} unique tags from content")
            return unique_tags

        except Exception as e:
            logger.error(f"NER extraction failed: {e}")
            raise
