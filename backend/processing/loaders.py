"""
Document loaders for different file types.
"""

from typing import List
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType


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

