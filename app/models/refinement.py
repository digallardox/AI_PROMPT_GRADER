"""Request and response models for message refinement."""
from pydantic import BaseModel, Field
from typing import List, Optional


class EvaluationScores(BaseModel):
    """Multi-criteria evaluation scores for a response."""
    empathy: int = Field(..., ge=1, le=5, description="Empathy score (1-5)")
    actionability: int = Field(..., ge=1, le=5, description="Actionability score (1-5)")
    safety: bool = Field(..., description="Safety check (True = safe, False = unsafe)")
    length_ok: bool = Field(..., description="Length check (True = under 500 chars)")
    personality_match: bool = Field(..., description="Personality match (True = matches traits)")


class RefinementCriteria(BaseModel):
    """Criteria for refining a response."""
    max_length: int = Field(default=500, description="Maximum response length in characters")
    tone: str = Field(default="warm", description="Desired tone (warm, supportive, professional)")
    check_safety: bool = Field(default=True, description="Whether to check for safety issues")
    personality_traits: List[str] = Field(default_factory=list, description="Companion personality traits to preserve")


class RefineRequest(BaseModel):
    """Request model for message refinement."""
    original_prompt: str = Field(..., description="Original system prompt used for the response")
    original_response: str = Field(..., max_length=5000, description="Original AI response to refine")
    criteria: RefinementCriteria = Field(default_factory=RefinementCriteria, description="Refinement criteria")


class RefineResponse(BaseModel):
    """Response model for message refinement."""
    refined_response: str = Field(..., description="Refined response text")
    was_improved: bool = Field(..., description="Whether the response was actually refined (True) or kept as-is (False)")
    evaluation_scores: Optional[EvaluationScores] = Field(default=None, description="Quality evaluation scores")
    changes: List[str] = Field(default_factory=list, description="List of improvements made")
