"""
Pydantic models for upload API endpoints.
"""

from pydantic import BaseModel
from typing import Optional


class UploadResponse(BaseModel):
    """Response model for upload endpoint."""
    message: str
    chunks: Optional[int] = None

