"""
Metadata cleaning and serialization utilities for ChromaDB compatibility.
"""

import json
from typing import Dict, Any


def clean_metadata_for_chromadb(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Clean metadata to ensure ChromaDB compatibility.
    
    ChromaDB only accepts simple types (str, int, float, bool, None).
    Complex types like dicts and lists are serialized to JSON strings.
    
    Args:
        metadata: Original metadata dictionary
        
    Returns:
        Cleaned metadata dictionary with all values as ChromaDB-compatible types
    """
    cleaned_metadata = {}
    
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool, type(None))):
            # Simple types can be stored directly
            cleaned_metadata[key] = value
        elif isinstance(value, (dict, list)):
            # Complex types (like dl_meta) need to be serialized to JSON string
            cleaned_metadata[key] = json.dumps(value) if value else None
        else:
            # Convert other types to string
            cleaned_metadata[key] = str(value) if value else None
    
    return cleaned_metadata

