"""
FastAPI server for RAG application.
Provides REST API endpoints for chat and file upload functionality.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any

# Import RAG functions from backend module
from backend.rag import run_pipeline

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


# Request/Response models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    question: str


class SourceInfo(BaseModel):
    """Source information model."""
    content: str
    metadata: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    answer: str
    sources: Optional[List[SourceInfo]] = None


@app.get("/api/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint to verify server is running.
    
    Returns:
        Dictionary with status message
    """
    return {"status": "healthy"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Chat endpoint that accepts questions and returns answers using RAG pipeline.
    
    Args:
        request: ChatRequest containing the question
        
    Returns:
        ChatResponse with answer and sources
        
    Raises:
        HTTPException: If question is empty or RAG pipeline fails
    """
    # Validate question
    if not request.question or not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )
    
    try:
        # Run RAG pipeline
        response = run_pipeline(request.question.strip())
        
        # Extract answer and context
        answer = response.get("answer", "")
        context_docs = response.get("context", [])
        
        # Format sources
        sources = []
        for doc in context_docs:
            sources.append(SourceInfo(
                content=doc.page_content,
                metadata=doc.metadata if hasattr(doc, 'metadata') else None
            ))
        
        return ChatResponse(
            answer=answer,
            sources=sources if sources else None
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    # Use import string format to enable reload functionality
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)

