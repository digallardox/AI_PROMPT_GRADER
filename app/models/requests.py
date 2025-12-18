"""Request models for API endpoints."""
from pydantic import BaseModel, Field
from typing import List


class CompanionSettings(BaseModel):
    """AI companion personality settings."""
    name: str
    avatar: str
    traits: List[str]


class ReflectionRequest(BaseModel):
    """Request model for reflection generation."""
    content: str = Field(..., max_length=10000, description="Journal entry content")
    companion: CompanionSettings


class TitleRequest(BaseModel):
    """Request model for title generation."""
    content: str = Field(..., max_length=1500, description="Journal entry content (truncated)")


class ChatMessage(BaseModel):
    """A single message in a conversation."""
    role: str = Field(..., pattern="^(user|assistant)$", description="Message role")
    content: str = Field(..., max_length=5000, description="Message content")


class ChatRequest(BaseModel):
    """Request model for chat conversation."""
    entryContent: str = Field(default="", max_length=4000, description="Journal entry context (empty for general conversation)")
    message: str = Field(..., max_length=1000, description="User's message")
    history: List[ChatMessage] = Field(default_factory=list, description="Conversation history")
    companion: CompanionSettings


class TagsRequest(BaseModel):
    """Request model for tag generation."""
    content: str = Field(..., max_length=10000, description="Journal entry content for tag extraction")
