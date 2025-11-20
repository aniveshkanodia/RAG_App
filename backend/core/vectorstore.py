"""
Vector database initialization and management.
"""

import logging
from typing import Dict, Optional
from langchain_chroma import Chroma
from backend.core.config import VECTOR_DB_COLLECTION_NAME, VECTOR_DB_PATH
from backend.core.embeddings import get_embeddings

logger = logging.getLogger(__name__)

# Global vectorstore instance
_vectordb = None


def get_vectorstore() -> Chroma:
    """Initialize and return vector database instance.
    
    Uses singleton pattern to ensure only one instance is created.
    
    Returns:
        Chroma vectorstore instance
    """
    global _vectordb
    
    if _vectordb is None:
        embeddings = get_embeddings()
        _vectordb = Chroma(
            collection_name=VECTOR_DB_COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=VECTOR_DB_PATH,
        )
    
    return _vectordb


def reset_vectorstore() -> None:
    """Reset the global vectorstore instance (useful for testing)."""
    global _vectordb
    _vectordb = None


def delete_documents_by_metadata(filter_dict: Dict) -> int:
    """Delete documents from vectorstore by metadata filter.
    
    Note: langchain_chroma.Chroma.delete() only accepts 'ids' parameter, not 'where'.
    This function queries the collection to find matching documents by metadata,
    then deletes them by their IDs.
    
    Args:
        filter_dict: Dictionary of metadata key-value pairs to filter by.
                    All conditions must match (AND logic).
                    Example: {"filename": "document.pdf", "content_hash": "abc123..."}
        
    Returns:
        Number of documents deleted
        
    Raises:
        RuntimeError: If vectorstore is not initialized
        Exception: If deletion fails
    """
    vectordb = get_vectorstore()
    
    if vectordb is None:
        raise RuntimeError("Vector database not initialized")
    
    try:
        # Access underlying ChromaDB collection which supports where filters
        # langchain_chroma wrapper doesn't expose where parameter in delete()
        collection = vectordb._collection
        
        # Format where clause for ChromaDB
        # ChromaDB requires operators ($eq, $ne, etc.) and $and for multiple conditions
        # Single condition: {"key": {"$eq": "value"}}
        # Multiple conditions: {"$and": [{"key1": {"$eq": "value1"}}, {"key2": {"$eq": "value2"}}]}
        if len(filter_dict) == 1:
            # Single condition - use $eq operator
            key, value = next(iter(filter_dict.items()))
            where_clause = {key: {"$eq": value}}
        else:
            # Multiple conditions - use $and operator
            where_clause = {
                "$and": [
                    {key: {"$eq": value}}
                    for key, value in filter_dict.items()
                ]
            }
        
        # First, query to find documents matching the metadata filter
        # ChromaDB's get() method accepts where parameter for filtering
        try:
            results = collection.get(where=where_clause)
            matching_ids = results.get("ids", []) if results else []
        except Exception as query_error:
            logger.error(f"Error querying documents with filter {filter_dict} (formatted as {where_clause}): {str(query_error)}")
            raise RuntimeError(f"Failed to query documents for deletion: {str(query_error)}") from query_error
        
        if not matching_ids:
            logger.info(f"No documents found matching filter: {filter_dict}")
            return 0
        
        # Delete documents by their IDs
        # ChromaDB's delete() accepts ids parameter
        try:
            result = collection.delete(ids=matching_ids)
            deleted_count = len(matching_ids)
            logger.info(f"Deleted {deleted_count} documents matching filter: {filter_dict}")
            return deleted_count
        except (TypeError, AttributeError) as delete_error:
            # Handle case where delete method signature is different
            error_msg = f"Error deleting documents: {str(delete_error)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from delete_error
        except Exception as delete_error:
            logger.error(f"Unexpected error deleting documents: {str(delete_error)}")
            raise
        
    except Exception as e:
        logger.error(f"Error deleting documents with filter {filter_dict}: {str(e)}")
        raise

