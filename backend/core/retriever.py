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
    """Retrieve documents with strict conversation filtering.
    
    Documents are only accessible in the chat session where they were uploaded.
    Chats without a conversation_id (new chats/home screen) have no document access.
    
    Args:
        question: User question for retrieval
        conversation_id: Conversation ID to filter documents by chat session.
                        If None, returns empty list (no documents accessible).
        k: Number of documents to retrieve (defaults to TOP_K from config)
        
    Returns:
        List of retrieved Document objects (always a list, never None).
        Returns empty list if conversation_id is None or no matching documents found.
    """
    if k is None:
        k = TOP_K
    
    # If no conversation_id provided, return empty list
    # Documents are only accessible in the chat where they were uploaded
    if conversation_id is None:
        logger.info("No conversation_id provided - returning empty list (documents only accessible in their upload chat)")
        return []
    
    vectordb = get_vectorstore()
    
    # Use similarity_search directly instead of retriever to ensure fresh embeddings
    # Retrieve more documents to account for conversation filtering
    # This ensures we have enough candidates after filtering by conversation_id
    retrieve_count = k * 2
    
    logger.info(f"Performing similarity search for question: '{question[:50]}...' with conversation_id: {conversation_id}, k={retrieve_count}")
    docs = vectordb.similarity_search(question, k=retrieve_count)
    
    # Ensure docs is a list (defensive check)
    if docs is None:
        docs = []
        logger.warning("similarity_search returned None, using empty list")
    elif not isinstance(docs, list):
        # Convert to list if it's not already
        docs = list(docs) if hasattr(docs, '__iter__') else []
        logger.warning(f"similarity_search returned non-list type: {type(docs)}, converted to list")
    
    # Validate document structure - ensure all items are Document objects with page_content
    valid_docs = []
    for doc in docs:
        if hasattr(doc, 'page_content') and hasattr(doc, 'metadata') and doc.page_content:
            valid_docs.append(doc)
    
    logger.info(f"Retrieved {len(valid_docs)} valid documents from similarity search")
    
    # Filter to only include documents that exactly match the conversation_id
    # Never falls back to unfiltered documents to maintain strict conversation isolation
    logger.info(f"Filtering documents by conversation_id: {conversation_id}")
    logger.info(f"Total valid docs before filtering: {len(valid_docs)}")
    
    # Debug: Log conversation_ids found in documents
    found_conversation_ids = [doc.metadata.get("conversation_id") for doc in valid_docs if hasattr(doc, 'metadata')]
    logger.info(f"Conversation IDs found in documents: {set(found_conversation_ids)}")
    
    # Only include documents that exactly match the conversation_id
    # Documents without conversation_id are NOT accessible (strict isolation)
    filtered_docs = [
        doc for doc in valid_docs 
        if doc.metadata.get("conversation_id") == conversation_id
    ]
    
    logger.info(f"Documents after filtering (exact conversation_id match): {len(filtered_docs)}")
    
    # Return filtered results
    return filtered_docs[:k]

