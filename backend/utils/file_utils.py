"""
File utility functions for hashing and file operations.
"""

import hashlib
import os
from typing import Optional


def compute_file_hash(file_path: str) -> str:
    """Compute SHA256 hash of file content.
    
    Args:
        file_path: Path to the file to hash
        
    Returns:
        Hexadecimal string representation of the SHA256 hash
        
    Raises:
        FileNotFoundError: If file does not exist
        IOError: If file cannot be read
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    sha256_hash = hashlib.sha256()
    
    # Read file in chunks to handle large files efficiently
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()


def get_file_size(file_path: str) -> int:
    """Get file size in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes
        
    Raises:
        FileNotFoundError: If file does not exist
        OSError: If file cannot be accessed
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    return os.path.getsize(file_path)

