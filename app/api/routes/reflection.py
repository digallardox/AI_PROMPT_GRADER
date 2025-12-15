"""Reflection generation endpoint."""
import json
import re
from fastapi import APIRouter
from app.models import ReflectionRequest, ReflectionResponse
from app.dependencies import ClaudeDep, PromptDep

router = APIRouter(tags=["reflection"])


def strip_markdown_json(text: str) -> str:
    """
    Strip markdown code fences from JSON response.

    Claude often wraps JSON in ```json ... ``` despite instructions not to.
    This helper removes those fences to allow clean JSON parsing.

    Args:
        text: Raw response text that may contain markdown fences

    Returns:
        Clean JSON string without markdown formatting
    """
    # Remove leading/trailing whitespace
    text = text.strip()

    # Remove markdown code fences (```json ... ``` or ``` ... ```)
    # Pattern: optional ```json, content, optional ```
    pattern = r'^```(?:json)?\s*\n?(.*?)\n?```$'
    match = re.match(pattern, text, re.DOTALL)

    if match:
        return match.group(1).strip()

    return text


@router.post("/reflection", response_model=ReflectionResponse)
async def generate_reflection(
    req: ReflectionRequest,
    claude: ClaudeDep,
    prompts: PromptDep,
):
    """
    Generate empathetic reflection and follow-up question for journal entry.

    Args:
        req: Reflection request containing entry content and companion settings
        claude: Claude service (injected)
        prompts: Prompt service (injected)

    Returns:
        ReflectionResponse: Generated reflection and follow-up question
    """
    # Build system prompt
    system_prompt = prompts.build_reflection_prompt(
        companion_name=req.companion.name,
        traits=req.companion.traits,
        content=req.content
    )

    # Call Claude
    response = await claude.chat(system_prompt, req.content)

    # Strip markdown code fences (Claude often adds them despite instructions)
    clean_response = strip_markdown_json(response)

    # Parse JSON response
    try:
        result = json.loads(clean_response)
        return ReflectionResponse(
            reflection=result["reflection"],
            question=result["question"]
        )
    except (json.JSONDecodeError, KeyError) as e:
        # Fallback if Claude doesn't return valid JSON
        # Log the error for debugging
        print(f"JSON parse error: {e}")
        print(f"Raw response: {response[:200]}...")
        print(f"Cleaned response: {clean_response[:200]}...")
        return ReflectionResponse(
            reflection=response[:500] if len(response) <= 500 else clean_response[:500],
            question="What else would you like to explore about this?"
        )
