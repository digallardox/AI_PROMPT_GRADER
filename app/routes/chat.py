"""Chat conversation endpoint."""
import asyncio
import logging
from fastapi import APIRouter
from app.models import ChatRequest, ChatResponse
from app.dependencies import ClaudeDep, PromptDep, RefinerDep, SettingsDep

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_about_entry(
    req: ChatRequest,
    claude: ClaudeDep,
    prompts: PromptDep,
    refiner: RefinerDep,
    settings: SettingsDep,
):
    """
    Have a conversation about a specific journal entry.

    Includes optional message refinement for quality improvement using constitutional AI.
    Refinement can be disabled via ENABLE_REFINEMENT environment variable.

    Args:
        req: Chat request containing entry context, message, history, and companion settings
        claude: Claude service (injected)
        prompts: Prompt service (injected)
        refiner: Refiner service (injected)
        settings: Application settings (injected)

    Returns:
        ChatResponse: Assistant's response message (refined if enabled and successful)
    """
    # Build system prompt with entry context
    system_prompt = prompts.build_chat_prompt(
        companion_name=req.companion.name,
        traits=req.companion.traits,
        entry_content=req.entryContent
    )

    # Format conversation history for Claude
    messages = [
        {
            "role": msg.role,
            "content": msg.content
            }
        for msg in req.history
    ]
    messages.append({"role": "user", "content": req.message})

    # Call Claude with conversation history to get initial response
    initial_response = await claude.chat(system_prompt, messages)

    # Refine response if enabled (with circuit breaker for resilience)
    final_response = initial_response
    if settings.enable_refinement:
        try:
            # Circuit breaker: timeout after configured duration
            logger.info("Attempting to refine response")
            refinement_result = await asyncio.wait_for(
                refiner.refine(
                    original_response=initial_response,
                    original_prompt=system_prompt,
                    personality_traits=req.companion.traits,
                    max_length=500,
                    tone="warm"
                ),
                timeout=settings.refinement_timeout
            )

            final_response = refinement_result["content"]

            if refinement_result["was_improved"]:
                logger.info(
                    "Response refined successfully",
                    extra={
                        "original_length": refinement_result["original_length"],
                        "refined_length": refinement_result["refined_length"]
                    }
                )
            else:
                logger.info("Response already excellent, no refinement needed")

        except asyncio.TimeoutError:
            logger.warning(
                f"Refinement timeout after {settings.refinement_timeout}s, using original response"
            )
            final_response = initial_response
        except Exception as e:
            logger.error(
                f"Refinement failed: {str(e)}, using original response",
                exc_info=True
            )
            final_response = initial_response
    else:
        logger.debug("Refinement disabled, using original response")

    return ChatResponse(
        message={"role": "assistant", "content": final_response}
    )
