"""
Retrieval logic with conversation filtering.
"""

import logging
from typing import List, Optional
from langchain_core.documents import Document
from backend.core.config import TOP_K
from backend.core.vectorstore import get_vectorstore

logger = logging.getLogger(__name__)


def retrieve_documents(
    question: str,
    conversation_id: Optional[str] = None,
    k: Optional[int] = None
) -> List[Document]:
    """Retrieve documents with optional conversation filtering.
    
    When conversation_id is provided, returns documents that either:
    - Match the conversation_id (conversation-scoped documents)
    - Have no conversation_id (global documents uploaded from home screen)
    
    This allows global documents to be accessible in all conversations while
    maintaining conversation isolation for conversation-scoped documents.
    
    Args:
        question: User question for retrieval
        conversation_id: Optional conversation ID to filter documents by chat session.
                        If provided, retrieves documents with matching conversation_id
                        or documents without conversation_id (global documents).
        k: Number of documents to retrieve (defaults to TOP_K from config)
        
    Returns:
        List of retrieved Document objects (always a list, never None)
    """
    if k is None:
        k = TOP_K
    
    vectordb = get_vectorstore()
    
    # Create retriever - retrieve more to account for filtering
    retriever = vectordb.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k * 2},  # Retrieve more to account for filtering
    )
    
    # Retrieve documents
    docs = retriever.invoke(question)
    
    # Ensure docs is a list (defensive check)
    if docs is None:
        docs = []
        logger.warning("Retriever.invoke returned None, using empty list")
    elif not isinstance(docs, list):
        # Convert to list if it's not already
        docs = list(docs) if hasattr(docs, '__iter__') else []
        logger.warning(f"Retriever.invoke returned non-list type: {type(docs)}, converted to list")
    
    # Validate document structure - ensure all items are Document objects with page_content
    valid_docs = []
    for doc in docs:
        if hasattr(doc, 'page_content') and hasattr(doc, 'metadata') and doc.page_content:
            valid_docs.append(doc)
    
    # Filter by conversation_id in Python if provided
    if conversation_id is not None:
        logger.info(f"Filtering documents by conversation_id: {conversation_id}")
        logger.info(f"Total valid docs before filtering: {len(valid_docs)}")
        
        # Debug: Log conversation_ids found in documents
        found_conversation_ids = [doc.metadata.get("conversation_id") for doc in valid_docs if hasattr(doc, 'metadata')]
        logger.info(f"Conversation IDs found in documents: {set(found_conversation_ids)}")
        
        # Include documents that match the conversation_id OR have no conversation_id (global documents)
        # This allows documents uploaded from home screen (no conversation_id) to be accessible
        # while still maintaining conversation isolation for conversation-scoped documents
        filtered_docs = [
            doc for doc in valid_docs 
            if doc.metadata.get("conversation_id") == conversation_id or doc.metadata.get("conversation_id") is None
        ]
        logger.info(f"Documents after filtering (matching conversation_id or global): {len(filtered_docs)}")
        
        # Return filtered results
        return filtered_docs[:k]
    else:
        # No filtering - return all documents
        logger.info(f"No conversation_id provided, returning all {len(valid_docs)} documents")
        return valid_docs[:k]

