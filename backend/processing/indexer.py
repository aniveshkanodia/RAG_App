"""
Indexing logic for adding documents to vector database.
"""

import os
import json
from typing import List, Optional
from langchain_core.documents import Document
from backend.core.vectorstore import get_vectorstore
from backend.utils.metadata import clean_metadata_for_chromadb


def generate_chunk_ids(base_filename: str, num_chunks: int) -> List[str]:
    """Generate chunk IDs based on filename with numeric suffix.
    
    Args:
        base_filename: Base filename (without path)
        num_chunks: Number of chunks to generate IDs for
        
    Returns:
        List of chunk IDs in format: {filename}_0, {filename}_1, etc.
    """
    # Sanitize filename to ensure valid ID format
    safe_filename = "".join(c if c.isalnum() or c in ('_', '-', '.') else '_' for c in base_filename)
    return [f"{safe_filename}_{i}" for i in range(num_chunks)]


def prepare_chunks_for_indexing(
    chunks: List[Document],
    conversation_id: Optional[str] = None,
    original_filename: Optional[str] = None,
    file_path: Optional[str] = None
) -> List[Document]:
    """Prepare document chunks for indexing by cleaning metadata.
    
    Args:
        chunks: List of Document chunks to prepare
        conversation_id: Optional conversation ID to add to metadata
        original_filename: Original filename from upload
        file_path: Path to the source file
        
    Returns:
        List of Document chunks with cleaned metadata
    """
    # Determine base filename
    if original_filename:
        base_filename = os.path.basename(original_filename)
    elif file_path:
        base_filename = os.path.basename(file_path)
    else:
        base_filename = "unknown"
    
    # Clean and prepare metadata for each chunk
    for chunk in chunks:
        # Clean metadata for ChromaDB compatibility
        cleaned_metadata = clean_metadata_for_chromadb(chunk.metadata)
        
        # Ensure source and filename are present
        if "source" not in cleaned_metadata:
            cleaned_metadata["source"] = file_path or ""
        if "filename" not in cleaned_metadata:
            cleaned_metadata["filename"] = base_filename
        
        # Add conversation_id to metadata if provided
        if conversation_id is not None:
            cleaned_metadata["conversation_id"] = conversation_id
        
        # Update chunk metadata with cleaned version
        chunk.metadata = cleaned_metadata
    
    return chunks


def index_documents(
    chunks: List[Document],
    chunk_ids: List[str]
) -> None:
    """Add document chunks to vector database.
    
    Args:
        chunks: List of Document chunks to index
        chunk_ids: List of IDs for the chunks (must match chunks length)
        
    Raises:
        RuntimeError: If vectorstore is not initialized
    """
    vectordb = get_vectorstore()
    
    if vectordb is None:
        raise RuntimeError("Vector database not initialized")
    
    # Add to vector database with custom IDs
    vectordb.add_documents(documents=chunks, ids=chunk_ids)

