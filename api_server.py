"""
FastAPI server for RAG application.
Provides REST API endpoints for chat and file upload functionality.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

# Initialize FastAPI app
app = FastAPI(
    title="RAG API Server",
    description="REST API for RAG chat and document upload functionality",
    version="1.0.0"
)

# Configure CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=False,  # Cannot use True with allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint to verify server is running.
    
    Returns:
        Dictionary with status message
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    # Use import string format to enable reload functionality
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)

