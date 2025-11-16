"""
Embedding model initialization and management.
"""

from langchain_ollama import OllamaEmbeddings
from backend.core.config import EMBEDDING_MODEL

# Global embedding instance
_embeddings = None


def get_embeddings() -> OllamaEmbeddings:
    """Initialize and return embedding model instance.
    
    Uses singleton pattern to ensure only one instance is created.
    
    Returns:
        OllamaEmbeddings instance
    """
    global _embeddings
    
    if _embeddings is None:
        _embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    
    return _embeddings


def reset_embeddings() -> None:
    """Reset the global embeddings instance (useful for testing)."""
    global _embeddings
    _embeddings = None

