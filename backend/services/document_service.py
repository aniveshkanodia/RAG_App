"""
Document processing service - Orchestrates document loading, chunking, and indexing.
"""

import os
from typing import Optional
from backend.processing.loaders import load_document
from backend.processing.chunkers import process_documents_for_chunking
from backend.processing.indexer import (
    generate_chunk_ids,
    prepare_chunks_for_indexing,
    index_documents
)


def process_and_index_file(
    file_path: str,
    conversation_id: Optional[str] = None,
    original_filename: Optional[str] = None
) -> str:
    """Process an uploaded file and add it to the vector database.
    
    This function orchestrates the complete document processing pipeline:
    1. Load document based on file type
    2. Chunk documents appropriately
    3. Prepare metadata and generate chunk IDs
    4. Index documents in vector database
    
    Args:
        file_path: Path to the uploaded file (may be temporary)
        conversation_id: Optional conversation ID to associate the file with a chat session
        original_filename: Original filename from upload (used for chunk IDs)
        
    Returns:
        Status message indicating success or error
    """
    if not file_path:
        return "Error: No file provided."
    
    try:
        # Determine base filename
        if original_filename:
            base_filename = os.path.basename(original_filename)
        else:
            base_filename = os.path.basename(file_path)
        
        # Extract file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Step 1: Load document
        documents = load_document(file_path, file_ext)
        
        # Step 2: Process documents for chunking
        chunks = process_documents_for_chunking(documents, file_ext)
        
        # Step 3: Generate chunk IDs
        chunk_ids = generate_chunk_ids(base_filename, len(chunks))
        
        # Step 4: Prepare chunks for indexing (clean metadata, add conversation_id)
        chunks = prepare_chunks_for_indexing(
            chunks,
            conversation_id=conversation_id,
            original_filename=original_filename,
            file_path=file_path
        )
        
        # Step 5: Index documents in vector database
        index_documents(chunks, chunk_ids)
        
        # Provide detailed status
        status = f"Successfully uploaded and indexed {len(chunks)} chunks from {base_filename}"
        # All DoclingLoader files are processed and ready for chat
        docling_supported = [".pdf", ".docx", ".doc", ".xlsx", ".xls"]
        if file_ext in docling_supported:
            status += "\n(Processed document ready for chat)"
        
        return status
    except Exception as e:
        return f"Error processing file: {str(e)}"

