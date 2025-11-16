"""
Configuration constants for RAG pipeline.
Centralizes all configuration values used across the application.
"""

# RAG pipeline configuration
TOP_K = 4  # Number of documents to retrieve

# Model configuration
EMBEDDING_MODEL = "qwen3-embedding:0.6b"
LLM_MODEL = "qwen3:0.6b"
LLM_KEEP_ALIVE = "2h"
LLM_TEMPERATURE = 0

# Vector database configuration
VECTOR_DB_COLLECTION_NAME = "documents"
VECTOR_DB_PATH = "./db/chroma_db"

# Chunking configuration (for non-Docling files)
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100

