"""Message refinement endpoint."""
import logging
from fastapi import APIRouter
from app.models.refinement import RefineRequest, RefineResponse
from app.dependencies import RefinerDep

logger = logging.getLogger(__name__)
router = APIRouter(tags=["refinement"])


@router.post("/refine", response_model=RefineResponse)
async def refine_message(
    req: RefineRequest,
    refiner: RefinerDep,
):
    """
    Refine an AI response to meet quality criteria.

    Uses constitutional AI approach with multi-criteria evaluation:
    - Empathy score (1-5)
    - Actionability score (1-5)
    - Safety check (pass/fail)
    - Length check (pass/fail)
    - Personality consistency (pass/fail)

    Args:
        req: Refinement request containing original prompt, response, and criteria
        refiner: Refiner service (injected)

    Returns:
        RefineResponse: Refined response with improvement metadata
    """
    logger.info(
        "Refining message",
        extra={
            "original_length": len(req.original_response),
            "max_length": req.criteria.max_length,
            "tone": req.criteria.tone
        }
    )

    # Call refiner service
    result = await refiner.refine(
        original_response=req.original_response,
        original_prompt=req.original_prompt,
        personality_traits=req.criteria.personality_traits,
        max_length=req.criteria.max_length,
        tone=req.criteria.tone
    )

    # Build response with improvement details
    changes = []
    if result["was_improved"]:
        length_diff = result["original_length"] - result["refined_length"]
        if abs(length_diff) > 10:
            if length_diff > 0:
                changes.append(f"Shortened by {length_diff} characters")
            else:
                changes.append(f"Extended by {abs(length_diff)} characters")
        changes.append("Improved clarity and empathy")

    return RefineResponse(
        refined_response=result["content"],
        was_improved=result["was_improved"],
        changes=changes,
        evaluation_scores=None  # TODO: Could parse scores from Claude response if needed
    )
