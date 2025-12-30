"""Service for refining AI responses using constitutional AI approach."""
import logging
from typing import List, Dict, Any
from anthropic import AsyncAnthropic
from app.config import Settings
from app.services.prompts.refine_prompt_builder import RefinePromptBuilder

logger = logging.getLogger(__name__)


class RefinerService:
    """Service for refining AI responses to meet quality criteria."""

    def __init__(self, settings: Settings):
        """
        Initialize Refiner service with settings.

        Args:
            settings: Application settings containing API key and refinement config

        Raises:
            ValueError: If ANTHROPIC_API_KEY is not set
        """
        if not settings.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not set. Please set it in .env file or environment."
            )

        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.refinement_model  # claude-3-5-haiku-20241022
        self.max_tokens = settings.refinement_max_tokens
        self.temperature = settings.refinement_temperature
        self.prompt_builder = RefinePromptBuilder()
        self.enabled = settings.enable_refinement

    async def refine(
        self,
        original_response: str,
        original_prompt: str,
        personality_traits: List[str],
        max_length: int = 500,
        tone: str = "warm"
    ) -> Dict[str, Any]:
        """
        Refine an AI response to meet quality criteria.

        Uses a constitutional AI approach with multi-criteria evaluation:
        - Empathy (1-5 score)
        - Actionability (1-5 score)
        - Safety (pass/fail)
        - Length (pass/fail)
        - Personality consistency (pass/fail)

        Args:
            original_response: The AI response to refine
            original_prompt: The system prompt used to generate the original response
            personality_traits: List of companion personality traits to preserve
            max_length: Maximum allowed response length in characters
            tone: Desired tone (warm, supportive, professional)

        Returns:
            Dict containing:
                - content: The refined response text (or original if already excellent)
                - was_improved: Boolean indicating if refinement was applied
                - original_length: Length of original response
                - refined_length: Length of refined response
        """
        if not self.enabled:
            logger.info("Refinement disabled, returning original response")
            return {
                "content": original_response,
                "was_improved": False,
                "original_length": len(original_response),
                "refined_length": len(original_response)
            }

        try:
            # Build refinement prompt using constitutional AI approach
            refinement_prompt = self.prompt_builder.build(
                original_prompt=original_prompt,
                original_response=original_response,
                personality_traits=personality_traits,
                max_length=max_length,
                tone=tone
            )

            # Call Claude (Haiku) to refine the response
            # Use a simple user message to trigger the refinement
            refined_text = await self.client.messages.create(
                model=self.model,
                system=refinement_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": "Please evaluate and refine the response if needed."
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            refined_response = refined_text.content[0].text.strip()

            # Detect if refinement actually changed the response
            # Claude might return the original if it's already excellent
            was_improved = refined_response != original_response.strip()

            # Log refinement details
            logger.info(
                "Refinement complete",
                extra={
                    "was_improved": was_improved,
                    "original_length": len(original_response),
                    "refined_length": len(refined_response),
                    "length_reduction": len(original_response) - len(refined_response),
                    "personality_traits": personality_traits
                }
            )

            return {
                "content": refined_response,
                "was_improved": was_improved,
                "original_length": len(original_response),
                "refined_length": len(refined_response)
            }

        except Exception as e:
            # If refinement fails for any reason, return original response
            logger.error(
                f"Refinement failed: {str(e)}, returning original response",
                exc_info=True
            )
            return {
                "content": original_response,
                "was_improved": False,
                "original_length": len(original_response),
                "refined_length": len(original_response),
                "error": str(e)
            }
