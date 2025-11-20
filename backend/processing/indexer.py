"""
Indexing logic for adding documents to vector database.
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Optional
from langchain_core.documents import Document
from backend.core.vectorstore import get_vectorstore, delete_documents_by_metadata
from backend.utils.metadata import clean_metadata_for_chromadb

logger = logging.getLogger(__name__)


def generate_chunk_ids(base_filename: str, num_chunks: int, content_hash: Optional[str] = None) -> List[str]:
    """Generate chunk IDs based on filename with numeric suffix.
    
    Includes content hash in ID to prevent collisions when different files
    sanitize to the same filename (e.g., "my-file.pdf" and "my_file.pdf").
    
    Args:
        base_filename: Base filename (without path)
        num_chunks: Number of chunks to generate IDs for
        content_hash: Optional content hash to include in IDs for uniqueness
        
    Returns:
        List of chunk IDs in format: {filename}_{hash}_{i} or {filename}_{i} if no hash
    """
    # Sanitize filename to ensure valid ID format
    safe_filename = "".join(c if c.isalnum() or c in ('_', '-', '.') else '_' for c in base_filename)
    
    # Include content hash prefix to ensure uniqueness across different files
    # Use first 8 characters of hash for brevity while maintaining uniqueness
    if content_hash:
        hash_prefix = content_hash[:8]
        return [f"{safe_filename}_{hash_prefix}_{i}" for i in range(num_chunks)]
    else:
        # Fallback to original format if hash not provided (backward compatibility)
        return [f"{safe_filename}_{i}" for i in range(num_chunks)]


def prepare_chunks_for_indexing(
    chunks: List[Document],
    conversation_id: Optional[str] = None,
    original_filename: Optional[str] = None,
    file_path: Optional[str] = None,
    content_hash: Optional[str] = None,
    upload_timestamp: Optional[datetime] = None,
    last_indexed_timestamp: Optional[datetime] = None
) -> List[Document]:
    """Prepare document chunks for indexing by cleaning metadata.
    
    Args:
        chunks: List of Document chunks to prepare
        conversation_id: Optional conversation ID to add to metadata
        original_filename: Original filename from upload
        file_path: Path to the source file
        content_hash: SHA256 hash of file content (for de-duplication)
        upload_timestamp: Timestamp when file was uploaded
        last_indexed_timestamp: Timestamp when file was last indexed
        
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
    
    # Use current time if timestamps not provided
    now = datetime.utcnow()
    upload_ts = (upload_timestamp or now).isoformat()
    indexed_ts = (last_indexed_timestamp or now).isoformat()
    
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
            logger.debug(f"Added conversation_id {conversation_id} to chunk metadata")
        else:
            logger.warning(f"No conversation_id provided for chunk - document will not be conversation-scoped")
        
        # Add document tracking metadata (mirrored from registry)
        if content_hash:
            cleaned_metadata["content_hash"] = content_hash
        cleaned_metadata["upload_timestamp"] = upload_ts
        cleaned_metadata["last_indexed_timestamp"] = indexed_ts
        
        # Update chunk metadata with cleaned version
        chunk.metadata = cleaned_metadata
    
    return chunks


def delete_document_chunks(filename: str, content_hash: Optional[str] = None) -> int:
    """Delete all chunks for a document from the vector database.
    
    Uses metadata filtering to find and delete chunks. If content_hash is provided,
    it's used for more precise deletion. Otherwise, deletion is by filename only.
    
    Args:
        filename: Filename to match
        content_hash: Optional content hash for more precise matching
        
    Returns:
        Number of chunks deleted
        
    Raises:
        RuntimeError: If vectorstore is not initialized
    """
    # Build metadata filter
    filter_dict = {"filename": filename}
    if content_hash:
        filter_dict["content_hash"] = content_hash
    
    try:
        deleted_count = delete_documents_by_metadata(filter_dict)
        logger.info(f"Deleted {deleted_count} chunks for document: {filename} (hash: {content_hash[:16] if content_hash else 'N/A'}...)")
        return deleted_count
    except Exception as e:
        logger.error(f"Error deleting chunks for {filename}: {str(e)}")
        raise


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

