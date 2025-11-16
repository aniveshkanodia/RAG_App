"""
FastAPI application entry point.
Initializes the FastAPI app and registers all routes.

This module should be run as a package module from the project root:
    python -m backend.main
    
Or use the entry point at the root:
    python run_server.py
"""

# When run directly (python backend/main.py), add project root to path BEFORE imports
import sys
from pathlib import Path

# Check if we're being run directly (not imported)
if __name__ == "__main__" or (len(sys.argv) > 0 and sys.argv[0].endswith('backend/main.py')):
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

# Now imports will work correctly
from backend.config.settings import API_HOST, API_PORT, API_RELOAD
from backend.config.logging_config import setup_logging

# Setup logging
setup_logging()

from fastapi import FastAPI, UploadFile, File, Form
from typing import Dict, Optional
from backend.api.routes import chat, upload
from backend.api.middleware import setup_cors
from backend.api.models.chat import ChatRequest, ChatResponse
from backend.api.models.upload import UploadResponse

# Initialize FastAPI app
app = FastAPI(
    title="RAG API Server",
    description="REST API for RAG chat and document upload functionality",
    version="1.0.0"
)

# Setup CORS
setup_cors(app)


@app.get("/api/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint to verify server is running.
    
    Returns:
        Dictionary with status message
    """
    return {"status": "healthy"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """Chat endpoint that accepts questions and returns answers using RAG pipeline."""
    return await chat.handle_chat(request)


@app.post("/api/upload", response_model=UploadResponse)
async def upload_endpoint(
    file: UploadFile = File(...),
    conversation_id: Optional[str] = Form(None)
) -> UploadResponse:
    """File upload endpoint that processes and indexes uploaded files."""
    return await upload.handle_upload(file, conversation_id)


if __name__ == "__main__":
    import uvicorn
    # Run the app directly (app is already imported above)
    # Note: For reload to work properly, use: python -m backend.main
    # Or use the root-level entry point: python run_server.py
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        reload=API_RELOAD
    )
