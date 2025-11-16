"""
Pydantic models for chat API endpoints.
"""

from pydantic import BaseModel
from typing import Dict, List, Optional, Any


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    question: str
    conversation_id: Optional[str] = None
    turn_index: Optional[int] = None


class SourceInfo(BaseModel):
    """Source information model."""
    content: str
    metadata: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    answer: str
    sources: Optional[List[SourceInfo]] = None

