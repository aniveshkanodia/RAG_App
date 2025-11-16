"""
Chat API route handlers.
"""

import uuid
import logging
from fastapi import HTTPException
from backend.api.models.chat import ChatRequest, ChatResponse, SourceInfo
from backend.services.rag_service import run_rag_pipeline
from backend.utils.chunking_strategy import get_chunking_strategy
from rag_logging.rag_logger import log_rag_turn, create_log_record

logger = logging.getLogger(__name__)

# In-memory store for conversation tracking
# Maps conversation_id -> turn_index
_conversation_turn_index: dict[str, int] = {}


async def handle_chat(request: ChatRequest) -> ChatResponse:
    """Chat endpoint handler that accepts questions and returns answers using RAG pipeline.
    
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
        # Run RAG pipeline with conversation_id for file filtering
        response = run_rag_pipeline(user_query, conversation_id=conversation_id)
        
        # Extract answer and context
        # run_rag_pipeline guarantees context is always a list (never None)
        answer = response.get("answer", "")
        context_docs = response.get("context", [])
        
        # Extract context texts for logging (with validation)
        context_texts = []
        for doc in context_docs:
            if hasattr(doc, 'page_content'):
                context_texts.append(doc.page_content)
            else:
                logger.warning(f"Document missing page_content attribute, skipping from context_texts")
        
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
        
        # Format sources with validation
        sources = []
        for doc in context_docs:
            try:
                # Validate document structure before processing
                if not hasattr(doc, 'page_content'):
                    continue
                
                # Get page_content
                page_content = doc.page_content
                if not page_content:
                    continue
                
                # Extract metadata safely
                metadata = doc.metadata if hasattr(doc, 'metadata') else None
                
                # Ensure metadata is a dict or None
                if metadata is not None and not isinstance(metadata, dict):
                    try:
                        metadata = dict(metadata) if hasattr(metadata, 'items') else None
                    except Exception:
                        metadata = None
                
                source_info = SourceInfo(
                    content=str(page_content),
                    metadata=metadata if isinstance(metadata, dict) else None
                )
                sources.append(source_info)
                
            except Exception as source_error:
                # Log error but continue processing other sources
                logger.error(f"Error creating source from document: {source_error}", exc_info=True)
                continue
        
        return ChatResponse(
            answer=answer,
            sources=sources if sources else None
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )

