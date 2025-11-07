"""
Document processing module.
Contains functions for loading, processing, and indexing documents.
"""

import os
import json
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, UnstructuredWordDocumentLoader
from langchain_core.documents import Document

# Docling imports
from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType

# Import rag module to access vectordb after initialization
import backend.rag as rag_module


def load_document(file_path: str) -> List[Document]:
    """Load a document based on its file extension.
    
    For PDF files, uses DoclingLoader to preserve structure.
    For other file types, uses standard loaders.
    
    Args:
        file_path: Path to the file to load
        
    Returns:
        List of Document objects from the file
        
    Raises:
        ValueError: If file type is not supported
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == ".pdf":
        loader = DoclingLoader(
            file_path=file_path,
            export_type=ExportType.DOC_CHUNKS  # Preserves structure with semantic chunking
        )
        documents = loader.load()
    elif file_ext == ".txt":
        loader = TextLoader(file_path)
        documents = loader.load()
    elif file_ext in [".docx", ".doc"]:
        loader = UnstructuredWordDocumentLoader(file_path)
        documents = loader.load()
    else:
        raise ValueError(
            f"Unsupported file type: {file_ext}. "
            f"Supported types: .pdf, .txt, .docx, .doc"
        )
    
    return documents


def process_documents_for_chunking(
    documents: List[Document], 
    file_path: str
) -> List[Document]:
    """Process documents for chunking based on the export type.
    
    For PDF files with DOC_CHUNKS mode, documents are already chunked by HybridChunker.
    For other document types, use standard text splitting.
    
    Args:
        documents: List of Document objects
        file_path: Path to the file (to determine processing mode)
        
    Returns:
        List of processed Document chunks
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # PDF files are already chunked by DoclingLoader with ExportType.DOC_CHUNKS
    if file_ext == ".pdf":
        return documents
    
    # For non-PDF files, use standard text splitting
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(documents)
    return chunks


def process_and_index_file(file_path: str) -> str:
    """Process an uploaded file and add it to the vector database.
    
    Args:
        file_path: Path to the uploaded file
        
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
        
        # Load document (PDFs use DoclingLoader automatically)
        documents = load_document(file_path)
        
        # Process documents for chunking
        chunks = process_documents_for_chunking(documents, file_path)
        
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
            
            # Ensure source and filename are present
            if "source" not in cleaned_metadata:
                cleaned_metadata["source"] = file_path
            if "filename" not in cleaned_metadata:
                cleaned_metadata["filename"] = os.path.basename(file_path)
            
            # Update chunk metadata with cleaned version
            chunk.metadata = cleaned_metadata
        
        # Add to existing vector database
        vectordb.add_documents(documents=chunks)  # type: ignore[misc]
        
        # Provide detailed status
        file_ext = os.path.splitext(file_path)[1].lower()
        status = f"Successfully uploaded and indexed {len(chunks)} chunks from {os.path.basename(file_path)}"
        if file_ext == ".pdf":
            status += "\n(Processed document ready for chat)"
        
        return status
    except Exception as e:
        return f"Error processing file: {str(e)}"

