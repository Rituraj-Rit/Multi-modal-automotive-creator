from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Request Models

class GenerateNarrativeRequest(BaseModel):
    """Request model for generating automotive narratives."""
    prompt: str = Field(..., description="The prompt describing the car concept", min_length=3)
    context: Optional[str] = Field(None, description="Optional context from previous conversations")
    style: Optional[str] = Field("detailed", description="Style of the narrative: brief, detailed, or marketing")


class GenerateImageRequest(BaseModel):
    """Request model for generating car images."""
    prompt: str = Field(..., description="The prompt describing the car design", min_length=3)
    size: Optional[str] = Field("1024x1024", description="Image size: 1024x1024, 1024x1792, or 1792x1024")
    quality: Optional[str] = Field("standard", description="Image quality: standard or hd")
    style: Optional[str] = Field("vivid", description="Image style: vivid or natural")
    enhance_prompt: Optional[bool] = Field(True, description="Whether to enhance the prompt using AI")


class GenerateBothRequest(BaseModel):
    """Request model for generating both narrative and image."""
    prompt: str = Field(..., description="The prompt describing the car concept", min_length=3)
    context: Optional[str] = Field(None, description="Optional context from previous conversations")
    enhance_prompt: Optional[bool] = Field(True, description="Whether to enhance the prompt using AI")
    image_size: Optional[str] = Field("1024x1024", description="Image size")
    image_quality: Optional[str] = Field("standard", description="Image quality")
    image_style: Optional[str] = Field("vivid", description="Image style")
    save_to_history: Optional[bool] = Field(True, description="Whether to save to history")


class ChatMessage(BaseModel):
    """Model for chat messages."""
    role: str = Field(..., description="Role: user, assistant, or system")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request model for chat functionality."""
    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    context: Optional[str] = Field(None, description="Optional context")


class SearchRequest(BaseModel):
    """Request model for searching history."""
    query: str = Field(..., description="Search query")
    n_results: Optional[int] = Field(5, description="Number of results to return")


class EnhancePromptRequest(BaseModel):
    """Request model for enhancing prompts."""
    prompt: str = Field(..., description="The prompt to enhance", min_length=3)


# Response Models

class NarrativeResponse(BaseModel):
    """Response model for narrative generation."""
    success: bool
    narrative: Optional[str] = None
    model: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    error: Optional[str] = None


class ImageResponse(BaseModel):
    """Response model for image generation."""
    success: bool
    image_url: Optional[str] = None
    revised_prompt: Optional[str] = None
    filename: Optional[str] = None
    model: Optional[str] = None
    error: Optional[str] = None


class GenerationResponse(BaseModel):
    """Response model for combined narrative and image generation."""
    success: bool
    prompt: str
    narrative: Optional[str] = None
    image_url: Optional[str] = None
    revised_prompt: Optional[str] = None
    record_id: Optional[str] = None
    error: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat functionality."""
    success: bool
    response: Optional[str] = None
    model: Optional[str] = None
    error: Optional[str] = None


class HistoryItem(BaseModel):
    """Model for history items."""
    id: str
    prompt: str
    narrative: str
    image_url: str
    created_at: str


class HistoryResponse(BaseModel):
    """Response model for history retrieval."""
    success: bool
    history: List[HistoryItem]
    count: int


class SearchResult(BaseModel):
    """Model for search results."""
    id: str
    document: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    distance: Optional[float] = None


class SearchResponse(BaseModel):
    """Response model for search functionality."""
    success: bool
    results: List[SearchResult]
    count: int


class EnhancePromptResponse(BaseModel):
    """Response model for prompt enhancement."""
    success: bool
    enhanced_prompt: Optional[str] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    timestamp: str
    services: Dict[str, str]
