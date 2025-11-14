"""
FastAPI server for RAG application.
Provides REST API endpoints for chat and file upload functionality.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import os
import tempfile
import re
import uuid
import logging

# Import RAG functions from backend module
from backend.rag import run_pipeline
from backend.document_processor import process_and_index_file
from rag_logging.rag_logger import log_rag_turn, create_log_record

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


# In-memory store for conversation tracking
# Maps conversation_id -> turn_index
_conversation_turn_index: Dict[str, int] = {}


def get_chunking_strategy(context_docs: List[Any]) -> str:
    """Determine chunking strategy identifier based on retrieved documents.
    
    Args:
        context_docs: List of retrieved document chunks
        
    Returns:
        Chunking strategy identifier string
    """
    # Check if documents have metadata indicating chunking strategy
    # PDFs chunked with DoclingLoader typically have dl_meta in metadata
    has_docling_meta = False
    has_fixed_chunking = False
    
    for doc in context_docs:
        if hasattr(doc, 'metadata') and doc.metadata:
            # Check for docling metadata (PDFs)
            if 'dl_meta' in doc.metadata:
                has_docling_meta = True
            # Check for source file extension to infer strategy
            source = doc.metadata.get('source', '')
            if source.endswith('.pdf'):
                has_docling_meta = True
            elif source.endswith(('.txt', '.docx', '.doc')):
                has_fixed_chunking = True
    
    # Determine strategy identifier
    if has_docling_meta and has_fixed_chunking:
        return "mixed_docling_semantic_and_fixed_1000_overlap_100"
    elif has_docling_meta:
        return "docling_semantic"
    elif has_fixed_chunking:
        return "fixed_1000_overlap_100"
    else:
        # Default fallback based on system configuration
        return "docling_semantic_for_pdf_fixed_1000_overlap_100_for_others"


# Request/Response models
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


class UploadResponse(BaseModel):
    """Response model for upload endpoint."""
    message: str
    chunks: Optional[int] = None


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
        request: ChatRequest containing the question, optional conversation_id and turn_index
        
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
    
    # Handle conversation tracking
    conversation_id = request.conversation_id
    if not conversation_id:
        # Generate new conversation ID if not provided
        conversation_id = str(uuid.uuid4())
        logger.info(f"Generated new conversation_id: {conversation_id}")
    
    # Handle turn index tracking
    turn_index = request.turn_index
    if turn_index is None:
        # Track turn index per conversation
        if conversation_id not in _conversation_turn_index:
            _conversation_turn_index[conversation_id] = 0
        else:
            _conversation_turn_index[conversation_id] += 1
        turn_index = _conversation_turn_index[conversation_id]
    
    user_query = request.question.strip()
    
    try:
        # Run RAG pipeline
        response = run_pipeline(user_query)
        
        # Extract answer and context
        answer = response.get("answer", "")
        context_docs = response.get("context", [])
        
        # Extract context texts for logging
        context_texts = [doc.page_content for doc in context_docs]
        
        # Determine chunking strategy
        chunking_strategy = get_chunking_strategy(context_docs)
        
        # Log RAG turn (non-blocking, failure-tolerant)
        try:
            log_record = create_log_record(
                conversation_id=conversation_id,
                turn_index=turn_index,
                user_query=user_query,
                answer=answer,
                contexts=context_texts,
                chunking_strategy=chunking_strategy
            )
            log_rag_turn(log_record)
        except Exception as log_error:
            # Log error but don't break the request
            logger.error(f"Failed to log RAG turn: {log_error}", exc_info=True)
        
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


@app.post("/api/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)) -> UploadResponse:
    """File upload endpoint that processes and indexes uploaded files.
    
    Args:
        file: Uploaded file (PDF, TXT, DOCX, or DOC)
        
    Returns:
        UploadResponse with success message and number of chunks indexed
        
    Raises:
        HTTPException: If file is invalid, unsupported type, or processing fails
    """
    # Validate file is provided
    if not file:
        raise HTTPException(
            status_code=400,
            detail="No file provided"
        )
    
    # Validate file extension
    file_ext = os.path.splitext(file.filename or "")[1].lower()
    supported_extensions = [".pdf", ".txt", ".docx", ".doc"]
    
    if file_ext not in supported_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Supported types: {', '.join(supported_extensions)}"
        )
    
    # Create temporary file to save uploaded file
    temp_file_path = None
    try:
        # Read file content
        file_content = await file.read()
        
        if not file_content:
            raise HTTPException(
                status_code=400,
                detail="File is empty"
            )
        
        # Create temporary file with original extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        # Process and index the file
        result_message = process_and_index_file(temp_file_path)
        
        # Extract number of chunks from result message if available
        chunks = None
        if "indexed" in result_message.lower():
            # Try to extract chunk count from message like "indexed 5 chunks"
            match = re.search(r'indexed\s+(\d+)\s+chunks?', result_message, re.IGNORECASE)
            if match:
                chunks = int(match.group(1))
        
        # Check if processing was successful
        if result_message.startswith("Error"):
            raise HTTPException(
                status_code=500,
                detail=result_message
            )
        
        return UploadResponse(
            message=result_message,
            chunks=chunks
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception:
                # Ignore errors during cleanup
                pass


if __name__ == "__main__":
    import uvicorn
    # Use import string format to enable reload functionality
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)

