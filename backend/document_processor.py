"""
Document processing module.
Contains functions for loading, processing, and indexing documents.
"""

import os
import json
from typing import List, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document

# Docling imports
from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType

# Import rag module to access vectordb after initialization
import backend.rag as rag_module


def load_document(file_path: str, file_ext: str) -> List[Document]:
    """Load a document based on its file extension.
    
    Uses DoclingLoader for all Docling-supported file types (PDF, DOCX, XLSX, etc.)
    to standardize chunking. Falls back to standard loaders for unsupported types.
    
    Args:
        file_path: Path to the file to load
        file_ext: File extension (e.g., ".pdf", ".txt") to determine loader type
        
    Returns:
        List of Document objects from the file
        
    Raises:
        ValueError: If file type is not supported
    """
    # File types supported by DoclingLoader (use ExportType.DOC_CHUNKS for consistent chunking)
    docling_supported = [".pdf", ".docx", ".doc", ".xlsx", ".xls"]
    
    if file_ext in docling_supported:
        loader = DoclingLoader(
            file_path=file_path,
            export_type=ExportType.DOC_CHUNKS  # Preserves structure with semantic chunking
        )
        documents = loader.load()
    elif file_ext == ".txt":
        # TXT files: fallback to TextLoader (Docling may not support plain text)
        loader = TextLoader(file_path)
        documents = loader.load()
    else:
        raise ValueError(
            f"Unsupported file type: {file_ext}. "
            f"Supported types: .pdf, .txt, .docx, .doc, .xlsx, .xls"
        )
    
    return documents


def process_documents_for_chunking(
    documents: List[Document], 
    file_ext: str
) -> List[Document]:
    """Process documents for chunking based on the export type.
    
    Files loaded with DoclingLoader (PDF, DOCX, XLSX, etc.) are already chunked
    by HybridChunker via ExportType.DOC_CHUNKS. For other file types (e.g., TXT),
    use standard text splitting.
    
    Args:
        documents: List of Document objects
        file_ext: File extension (e.g., ".pdf", ".txt") to determine processing mode
        
    Returns:
        List of processed Document chunks
    """
    # File types that use DoclingLoader are already chunked via ExportType.DOC_CHUNKS
    docling_supported = [".pdf", ".docx", ".doc", ".xlsx", ".xls"]
    
    if file_ext in docling_supported:
        # Documents are already chunked by DoclingLoader with HybridChunker
        return documents
    
    # For non-Docling files (e.g., TXT), use standard text splitting
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(documents)
    return chunks


def process_and_index_file(file_path: str, conversation_id: Optional[str] = None, original_filename: Optional[str] = None) -> str:
    """Process an uploaded file and add it to the vector database.
    
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
        # Ensure RAG is initialized (this also initializes vectordb)
        rag_module.init_rag()
        
        # Get vectordb from the module after initialization
        vectordb = rag_module.vectordb
        
        # Ensure vectordb is available
        if vectordb is None:  # type: ignore[misc]
            return "Error: Vector database not initialized."
        
        # Use original filename if provided, otherwise fall back to file_path basename
        if original_filename:
            base_filename = os.path.basename(original_filename)
        else:
            base_filename = os.path.basename(file_path)
        
        # Extract file extension once for use in multiple functions
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Load document (PDFs use DoclingLoader automatically)
        documents = load_document(file_path, file_ext)
        
        # Process documents for chunking
        chunks = process_documents_for_chunking(documents, file_ext)
        
        # Generate IDs based on original filename with simple numeric suffix
        # Format: {filename}_0, {filename}_1, etc.
        # Sanitize filename to ensure valid ID format
        safe_filename = "".join(c if c.isalnum() or c in ('_', '-', '.') else '_' for c in base_filename)
        chunk_ids = [f"{safe_filename}_{i}" for i in range(len(chunks))]
        
        # Add metadata about the source file if not present
        # Note: ChromaDB only accepts simple types (str, int, float, bool, None)
        # So we need to serialize complex metadata like dl_meta to JSON strings
        for chunk in chunks:
            # Serialize complex metadata to JSON strings for ChromaDB compatibility
            cleaned_metadata = {}
            for key, value in chunk.metadata.items():
                if isinstance(value, (str, int, float, bool, type(None))):
                    # Simple types can be stored directly
                    cleaned_metadata[key] = value
                elif isinstance(value, (dict, list)):
                    # Complex types (like dl_meta) need to be serialized to JSON string
                    cleaned_metadata[key] = json.dumps(value) if value else None
                else:
                    # Convert other types to string
                    cleaned_metadata[key] = str(value) if value else None
            
            # Ensure source and filename are present (use original filename)
            if "source" not in cleaned_metadata:
                cleaned_metadata["source"] = file_path
            if "filename" not in cleaned_metadata:
                cleaned_metadata["filename"] = base_filename
            
            # Add conversation_id to metadata if provided
            # This allows filtering documents by chat session
            if conversation_id is not None:
                cleaned_metadata["conversation_id"] = conversation_id
            
            # Update chunk metadata with cleaned version
            chunk.metadata = cleaned_metadata
        
        # Add to existing vector database with custom IDs based on original filename
        vectordb.add_documents(documents=chunks, ids=chunk_ids)  # type: ignore[misc]
        
        # Provide detailed status
        status = f"Successfully uploaded and indexed {len(chunks)} chunks from {base_filename}"
        # All DoclingLoader files are processed and ready for chat
        docling_supported = [".pdf", ".docx", ".doc", ".xlsx", ".xls"]
        if file_ext in docling_supported:
            status += "\n(Processed document ready for chat)"
        
        return status
    except Exception as e:
        return f"Error processing file: {str(e)}"

