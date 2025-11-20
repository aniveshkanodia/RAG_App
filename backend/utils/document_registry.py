"""
Document registry for tracking indexed documents in Supabase.
Provides CRUD operations for document metadata tracking.

Row Level Security (RLS):
This module uses the Supabase anon key for authentication. RLS policies must be
configured on the 'documents' table to allow the anon role to perform:
- SELECT: For reading documents (get_document_by_hash, get_document_by_filename)
- INSERT: For registering new documents (register_document)
- UPDATE: For updating document metadata (update_document)
- DELETE: For deleting documents (delete_document)

See migration: add_rls_policies_for_documents
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from supabase import create_client, Client
from backend.core.config import SUPABASE_URL, SUPABASE_ANON_KEY

logger = logging.getLogger(__name__)

# Global Supabase client instance
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Initialize and return Supabase client instance.
    
    Uses singleton pattern to ensure only one instance is created.
    Validation of environment variables is deferred here (not at module import time)
    to allow graceful degradation if Supabase is unavailable.
    
    Returns:
        Supabase client instance
        
    Raises:
        RuntimeError: If Supabase URL or key is not configured
    """
    global _supabase_client
    
    if _supabase_client is None:
        # Validate required environment variables (deferred from config.py)
        if not SUPABASE_URL:
            error_msg = (
                "SUPABASE_URL environment variable is required. "
                "Please set it in your .env file or environment."
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        if not SUPABASE_ANON_KEY:
            error_msg = (
                "SUPABASE_ANON_KEY environment variable is required. "
                "Please set it in your .env file or environment. "
                "Never commit authentication tokens to version control."
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        try:
            _supabase_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            logger.info(f"Supabase client initialized for project: {SUPABASE_URL}")
        except Exception as e:
            error_msg = f"Failed to initialize Supabase client: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    return _supabase_client


def get_document_by_hash(content_hash: str) -> Optional[Dict]:
    """Get document by content hash.
    
    Args:
        content_hash: SHA256 hash of the file content
        
    Returns:
        Document record as dictionary, or None if not found
        
    Raises:
        RuntimeError: If Supabase client cannot be initialized or RLS policy blocks access
    """
    try:
        client = get_supabase_client()
        result = client.table("documents").select("*").eq("content_hash", content_hash).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        error_msg = str(e).lower()
        # Check for RLS-related errors
        if "row-level security" in error_msg or "policy" in error_msg or "permission denied" in error_msg:
            logger.error(f"RLS policy error getting document by hash {content_hash[:16]}...: {str(e)}")
            raise RuntimeError(
                "Access denied by Row Level Security policy. "
                "Please ensure RLS policies allow SELECT operations for the anon role."
            ) from e
        logger.error(f"Error getting document by hash {content_hash[:16]}...: {str(e)}")
        raise


def get_document_by_filename(filename: str) -> List[Dict]:
    """Get all documents with the same filename (multiple versions possible).
    
    Args:
        filename: Filename to search for
        
    Returns:
        List of document records (may be empty)
        
    Raises:
        RuntimeError: If Supabase client cannot be initialized or RLS policy blocks access
    """
    try:
        client = get_supabase_client()
        result = client.table("documents").select("*").eq("filename", filename).execute()
        
        return result.data if result.data else []
    except Exception as e:
        error_msg = str(e).lower()
        # Check for RLS-related errors
        if "row-level security" in error_msg or "policy" in error_msg or "permission denied" in error_msg:
            logger.error(f"RLS policy error getting documents by filename {filename}: {str(e)}")
            raise RuntimeError(
                "Access denied by Row Level Security policy. "
                "Please ensure RLS policies allow SELECT operations for the anon role."
            ) from e
        logger.error(f"Error getting documents by filename {filename}: {str(e)}")
        raise


def register_document(
    filename: str,
    content_hash: str,
    file_size: int,
    chunk_count: int,
    conversation_id: Optional[str] = None,
    upload_timestamp: Optional[datetime] = None,
    last_indexed_timestamp: Optional[datetime] = None
) -> Dict:
    """Register a new document in the registry.
    
    Args:
        filename: Original filename
        content_hash: SHA256 hash of file content
        file_size: File size in bytes
        chunk_count: Number of chunks created from the document
        conversation_id: Optional conversation ID to associate with the document
        upload_timestamp: Timestamp when file was uploaded (defaults to now)
        last_indexed_timestamp: Timestamp when file was last indexed (defaults to now)
        
    Returns:
        Created document record as dictionary
        
    Raises:
        RuntimeError: If Supabase client cannot be initialized
        Exception: If document with same hash already exists (should use update_document instead)
    """
    try:
        client = get_supabase_client()
        # Use provided timestamps or default to now (ensures consistency with chunk metadata)
        now = datetime.utcnow()
        upload_ts = (upload_timestamp or now).isoformat()
        indexed_ts = (last_indexed_timestamp or now).isoformat()
        
        data = {
            "filename": filename,
            "content_hash": content_hash,
            "file_size": file_size,
            "upload_timestamp": upload_ts,
            "last_indexed_timestamp": indexed_ts,
            "chunk_count": chunk_count,
            "conversation_id": conversation_id
        }
        
        result = client.table("documents").insert(data).execute()
        
        if result.data and len(result.data) > 0:
            logger.info(f"Registered document: {filename} (hash: {content_hash[:16]}...)")
            return result.data[0]
        else:
            raise RuntimeError("Failed to register document: no data returned")
    except Exception as e:
        error_msg = str(e).lower()
        # Check for RLS-related errors
        if "row-level security" in error_msg or "policy" in error_msg or "permission denied" in error_msg:
            logger.error(f"RLS policy error registering document {filename}: {str(e)}")
            raise RuntimeError(
                "Access denied by Row Level Security policy. "
                "Please ensure RLS policies allow INSERT operations for the anon role."
            ) from e
        logger.error(f"Error registering document {filename}: {str(e)}")
        raise


def update_document(
    content_hash: str,
    chunk_count: int,
    last_indexed: Optional[datetime] = None
) -> Dict:
    """Update an existing document's indexing information.
    
    Args:
        content_hash: SHA256 hash of file content (identifies the document)
        chunk_count: Updated number of chunks
        last_indexed: Optional timestamp for last indexing (defaults to now)
        
    Returns:
        Updated document record as dictionary
        
    Raises:
        RuntimeError: If Supabase client cannot be initialized or document not found
    """
    try:
        client = get_supabase_client()
        
        update_data = {
            "chunk_count": chunk_count,
            "last_indexed_timestamp": (last_indexed or datetime.utcnow()).isoformat()
        }
        
        result = client.table("documents").update(update_data).eq("content_hash", content_hash).execute()
        
        if result.data and len(result.data) > 0:
            logger.info(f"Updated document with hash: {content_hash[:16]}...")
            return result.data[0]
        else:
            raise RuntimeError(f"Document with hash {content_hash[:16]}... not found for update")
    except Exception as e:
        error_msg = str(e).lower()
        # Check for RLS-related errors
        if "row-level security" in error_msg or "policy" in error_msg or "permission denied" in error_msg:
            logger.error(f"RLS policy error updating document with hash {content_hash[:16]}...: {str(e)}")
            raise RuntimeError(
                "Access denied by Row Level Security policy. "
                "Please ensure RLS policies allow UPDATE operations for the anon role."
            ) from e
        logger.error(f"Error updating document with hash {content_hash[:16]}...: {str(e)}")
        raise


def delete_document(content_hash: str) -> None:
    """Delete a document from the registry.
    
    Args:
        content_hash: SHA256 hash of file content (identifies the document)
        
    Raises:
        RuntimeError: If Supabase client cannot be initialized
    """
    try:
        client = get_supabase_client()
        result = client.table("documents").delete().eq("content_hash", content_hash).execute()
        
        logger.info(f"Deleted document from registry: {content_hash[:16]}...")
    except Exception as e:
        error_msg = str(e).lower()
        # Check for RLS-related errors
        if "row-level security" in error_msg or "policy" in error_msg or "permission denied" in error_msg:
            logger.error(f"RLS policy error deleting document with hash {content_hash[:16]}...: {str(e)}")
            raise RuntimeError(
                "Access denied by Row Level Security policy. "
                "Please ensure RLS policies allow DELETE operations for the anon role."
            ) from e
        logger.error(f"Error deleting document with hash {content_hash[:16]}...: {str(e)}")
        raise


def get_all_chunk_ids_for_document(content_hash: str) -> List[str]:
    """Get all chunk IDs for a document.
    
    Note: ChromaDB doesn't store chunk IDs in a queryable way, so we reconstruct
    them from the document record. Chunk IDs follow the pattern: {filename}_{hash}_{i}
    where hash is the first 8 characters of content_hash and i ranges from 0 to chunk_count-1.
    
    Args:
        content_hash: SHA256 hash of file content
        
    Returns:
        List of chunk IDs for the document
        
    Raises:
        RuntimeError: If document not found
    """
    doc = get_document_by_hash(content_hash)
    if not doc:
        raise RuntimeError(f"Document with hash {content_hash[:16]}... not found")
    
    filename = doc["filename"]
    chunk_count = doc["chunk_count"]
    
    # Sanitize filename to match the pattern used in generate_chunk_ids
    safe_filename = "".join(c if c.isalnum() or c in ('_', '-', '.') else '_' for c in filename)
    
    # Include hash prefix to match the updated generate_chunk_ids format
    hash_prefix = content_hash[:8]
    
    return [f"{safe_filename}_{hash_prefix}_{i}" for i in range(chunk_count)]

