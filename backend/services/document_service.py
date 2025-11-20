"""
Document processing service - Orchestrates document loading, chunking, and indexing.
"""

import os
import logging
from datetime import datetime
from typing import Optional
from backend.processing.loaders import load_document
from backend.processing.chunkers import process_documents_for_chunking
from backend.processing.indexer import (
    generate_chunk_ids,
    prepare_chunks_for_indexing,
    index_documents,
    delete_document_chunks
)
from backend.utils.file_utils import compute_file_hash, get_file_size
from backend.utils.document_registry import (
    get_document_by_hash,
    get_document_by_filename,
    register_document,
    update_document,
    delete_document
)

logger = logging.getLogger(__name__)


def process_and_index_file(
    file_path: str,
    conversation_id: Optional[str] = None,
    original_filename: Optional[str] = None
) -> str:
    """Process an uploaded file and add it to the vector database.
    
    This function orchestrates the complete document processing pipeline with
    de-duplication and incremental updates:
    1. Compute file hash and check registry
    2. Skip if same hash exists (duplicate)
    3. Delete old chunks if filename matches but hash differs (update)
    4. Load and chunk document
    5. Index new chunks
    6. Register/update document in registry
    
    Args:
        file_path: Path to the uploaded file (may be temporary)
        conversation_id: Optional conversation ID to associate the file with a chat session
        original_filename: Original filename from upload (used for chunk IDs)
        
    Returns:
        Status message indicating success, skip, or error
    """
    if not file_path:
        return "Error: No file provided."
    
    try:
        # Determine base filename
        if original_filename:
            base_filename = os.path.basename(original_filename)
        else:
            base_filename = os.path.basename(file_path)
        
        # Step 0: Compute file hash and size (before processing)
        logger.info(f"Computing hash for file: {base_filename}")
        logger.info(f"Conversation ID for this upload: {conversation_id}")
        content_hash = compute_file_hash(file_path)
        file_size = get_file_size(file_path)
        
        # Check registry for existing document by hash
        # Wrap in try-except to handle Supabase/RLS errors gracefully
        existing_doc = None
        old_hash = None
        try:
            existing_doc = get_document_by_hash(content_hash)
            
            if existing_doc:
                # Same content hash = exact duplicate, skip processing
                logger.info(f"Document with hash {content_hash[:16]}... already indexed, skipping")
                return f"Document '{base_filename}' already indexed (duplicate content detected)."
            
            # Check if document with same filename exists but different hash (update scenario)
            existing_by_filename = get_document_by_filename(base_filename)
            
            if existing_by_filename:
                # Find document with same filename but different hash
                for doc in existing_by_filename:
                    if doc["content_hash"] != content_hash:
                        old_hash = doc["content_hash"]
                        logger.info(f"Found existing document '{base_filename}' with different hash, will update")
                        break
        except RuntimeError as rls_error:
            # RLS or Supabase connection error - log but continue with indexing
            # This allows graceful degradation: indexing works even if registry is unavailable
            error_msg = str(rls_error).lower()
            if "row-level security" in error_msg or "policy" in error_msg or "access denied" in error_msg:
                logger.warning(
                    f"RLS policy error accessing registry for {base_filename}. "
                    f"Continuing with indexing (duplicate detection disabled). Error: {str(rls_error)}"
                )
            else:
                logger.warning(
                    f"Supabase registry unavailable for {base_filename}. "
                    f"Continuing with indexing (duplicate detection disabled). Error: {str(rls_error)}"
                )
        except Exception as registry_error:
            # Any other registry error - log but continue
            logger.warning(
                f"Registry error for {base_filename}. "
                f"Continuing with indexing (duplicate detection disabled). Error: {str(registry_error)}"
            )
        
        # If update scenario, delete old chunks and old registry entry
        if old_hash:
            # Delete old chunks from ChromaDB (best-effort, continue even if fails)
            try:
                logger.info(f"Deleting old chunks for document: {base_filename}")
                deleted_count = delete_document_chunks(base_filename, old_hash)
                logger.info(f"Deleted {deleted_count} old chunks")
            except Exception as chunk_delete_error:
                # Log but continue - system should attempt re-indexing despite deletion failure
                # This implements the best-effort approach: new chunks will be indexed even if
                # old chunks couldn't be deleted (may result in duplicates, but system doesn't crash)
                logger.warning(
                    f"Failed to delete old chunks for document {base_filename} (hash: {old_hash[:16]}...): {str(chunk_delete_error)}. "
                    f"Continuing with re-indexing (may result in duplicate chunks)."
                )
            
            # Delete old registry entry to prevent orphaned records (best-effort)
            try:
                delete_document(old_hash)
                logger.info(f"Deleted old registry entry for hash: {old_hash[:16]}...")
            except Exception as registry_delete_error:
                # Log but continue - old chunks deletion may have succeeded, new document will be registered
                logger.warning(
                    f"Failed to delete old registry entry for hash {old_hash[:16]}...: {str(registry_delete_error)}. "
                    f"Continuing with new document registration."
                )
        
        # Extract file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Step 1: Load document
        documents = load_document(file_path, file_ext)
        
        # Step 2: Process documents for chunking
        chunks = process_documents_for_chunking(documents, file_ext)
        
        # Step 3: Generate chunk IDs (include content_hash to prevent collisions)
        chunk_ids = generate_chunk_ids(base_filename, len(chunks), content_hash=content_hash)
        
        # Step 4: Prepare chunks for indexing with tracking metadata
        now = datetime.utcnow()
        chunks = prepare_chunks_for_indexing(
            chunks,
            conversation_id=conversation_id,
            original_filename=original_filename,
            file_path=file_path,
            content_hash=content_hash,
            upload_timestamp=now,
            last_indexed_timestamp=now
        )
        
        # Step 5: Index documents in vector database
        index_documents(chunks, chunk_ids)
        
        # Step 6: Register or update document in registry
        # Use the same timestamps as chunk metadata to ensure consistency
        try:
            # Try to register new document with timestamps matching chunk metadata
            register_document(
                filename=base_filename,
                content_hash=content_hash,
                file_size=file_size,
                chunk_count=len(chunks),
                conversation_id=conversation_id,
                upload_timestamp=now,
                last_indexed_timestamp=now
            )
        except Exception as reg_error:
            # If registration fails (e.g., unique constraint), try update instead
            logger.warning(f"Registration failed, attempting update: {str(reg_error)}")
            try:
                # Pass last_indexed timestamp to ensure consistency with chunk metadata
                update_document(
                    content_hash=content_hash,
                    chunk_count=len(chunks),
                    last_indexed=now
                )
            except Exception as update_error:
                logger.error(f"Failed to update document in registry: {str(update_error)}")
                # Continue even if registry update fails (best effort)
        
        # Provide detailed status
        if old_hash:
            status = f"Successfully updated and re-indexed {len(chunks)} chunks from {base_filename}"
        else:
            status = f"Successfully uploaded and indexed {len(chunks)} chunks from {base_filename}"
        
        # All DoclingLoader files are processed and ready for chat
        docling_supported = [".pdf", ".docx", ".doc", ".xlsx", ".xls"]
        if file_ext in docling_supported:
            status += "\n(Processed document ready for chat)"
        
        return status
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}", exc_info=True)
        return f"Error processing file: {str(e)}"

