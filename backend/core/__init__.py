"""
Core RAG pipeline components.
"""

# Initialize components on import to ensure they're ready
from backend.core.config import (
    TOP_K,
    EMBEDDING_MODEL,
    LLM_MODEL,
    VECTOR_DB_COLLECTION_NAME,
    VECTOR_DB_PATH,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)

# Note: We don't initialize embeddings/vectorstore/llm here to avoid
# circular imports. They are initialized lazily when first accessed.

