"""
Chunking strategy detection utilities.
"""

from typing import List, Any


def get_chunking_strategy(context_docs: List[Any]) -> str:
    """Determine chunking strategy identifier based on retrieved documents.
    
    All files loaded with DoclingLoader (PDF, DOCX, XLSX, etc.) use unified
    Docling chunking via HybridChunker. TXT files may use fixed-size chunking.
    
    Args:
        context_docs: List of retrieved document chunks
        
    Returns:
        Chunking strategy identifier string
    """
    # Check if documents have metadata indicating chunking strategy
    # Files chunked with DoclingLoader typically have dl_meta in metadata
    has_docling_meta = False
    has_fixed_chunking = False
    
    # Docling-supported file extensions
    docling_extensions = ('.pdf', '.docx', '.doc', '.xlsx', '.xls')
    
    for doc in context_docs:
        if hasattr(doc, 'metadata') and doc.metadata:
            # Check for docling metadata (indicates DoclingLoader was used)
            if 'dl_meta' in doc.metadata:
                has_docling_meta = True
            # Check for source file extension to infer strategy
            source = doc.metadata.get('source', '')
            if source.endswith(docling_extensions):
                has_docling_meta = True
            elif source.endswith('.txt'):
                has_fixed_chunking = True
    
    # Determine strategy identifier
    if has_docling_meta and has_fixed_chunking:
        return "docling_hybrid_unified_with_txt_fallback"
    elif has_docling_meta:
        return "docling_hybrid_unified"
    elif has_fixed_chunking:
        return "fixed_1000_overlap_100"
    else:
        # Default fallback - assume unified docling chunking
        return "docling_hybrid_unified"

