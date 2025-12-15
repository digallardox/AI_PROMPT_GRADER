"""Response models for API endpoints."""
from pydantic import BaseModel, Field
from typing import List


class ReflectionResponse(BaseModel):
    """Response model for reflection generation."""
    reflection: str = Field(..., description="Empathetic reflection (≤500 chars)")
    question: str = Field(..., description="Follow-up question (≤200 chars)")


class TitleResponse(BaseModel):
    """Response model for title generation."""
    title: str = Field(..., description="Generated title (5-10 words)")


class ChatResponse(BaseModel):
    """Response model for chat conversation."""
    message: dict = Field(..., description="Assistant's response message")


class TagsResponse(BaseModel):
    """Response model for tag generation."""
    tags: List[str] = Field(..., description="Extracted named entities/tags from content")
