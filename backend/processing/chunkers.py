"""
Chunking strategies for different document types.
"""

from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from backend.core.config import CHUNK_SIZE, CHUNK_OVERLAP


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
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(documents)
    return chunks

