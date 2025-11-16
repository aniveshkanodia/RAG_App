"""
FastAPI server for RAG application (legacy entry point).
This file is kept for backward compatibility.
New code should use backend.main instead.

To run the server:
    uvicorn api_server:app --reload
    OR
    python backend/main.py
"""

# Import app from the new structure
from backend.main import app

# Re-export for backward compatibility
__all__ = ["app"]
