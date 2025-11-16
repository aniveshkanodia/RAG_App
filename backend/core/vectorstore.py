"""
Vector database initialization and management.
"""

from langchain_chroma import Chroma
from backend.core.config import VECTOR_DB_COLLECTION_NAME, VECTOR_DB_PATH
from backend.core.embeddings import get_embeddings

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

