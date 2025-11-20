#!/usr/bin/env python3
"""
Standalone script to clear all data from ChromaDB.

This script:
1. Resets the global vectorstore cache
2. Deletes the existing ChromaDB collection
3. Optionally deletes the entire database directory

Note: The collection and directory are NOT recreated. They will be automatically
created by get_vectorstore() when needed.

Usage:
    python clear_chroma_db.py           # Clear cache and collection only
    python clear_chroma_db.py --full    # Also delete entire database directory
"""

import os
import sys
import shutil
import argparse
from pathlib import Path


def clear_cache():
    """Reset the global vectorstore cache instance."""
    try:
        from backend.core.vectorstore import reset_vectorstore
        
        print("Resetting vectorstore cache...")
        reset_vectorstore()
        print("✓ Cache cleared successfully")
        return True
    except ImportError as e:
        print(f"❌ Error: Missing required package: {e}")
        print("Please install required packages: pip install langchain-chroma langchain-ollama")
        return False
    except Exception as e:
        print(f"❌ Error clearing cache: {e}")
        return False


def clear_collection():
    """Clear the ChromaDB collection programmatically."""
    try:
        from backend.core.embeddings import get_embeddings
        from backend.core.vectorstore import get_vectorstore
        
        print("Initializing ChromaDB connection...")
        
        # Initialize embeddings (needed for ChromaDB)
        embeddings = get_embeddings()
        
        # Connect to existing ChromaDB instance
        vectordb = get_vectorstore()
        
        print("Deleting collection...")
        
        # Delete the collection
        try:
            vectordb.delete_collection()
            print("✓ Collection deleted successfully")
        except Exception as e:
            error_msg = str(e).lower()
            if "does not exist" in error_msg or "not found" in error_msg:
                print("⚠ Collection does not exist (may already be empty)")
            else:
                raise
        return True
        
    except ImportError as e:
        print(f"❌ Error: Missing required package: {e}")
        print("Please install required packages: pip install langchain-chroma langchain-ollama")
        return False
    except Exception as e:
        print(f"❌ Error clearing collection: {e}")
        return False


def delete_directory():
    """Delete the entire ChromaDB directory."""
    try:
        from backend.core.config import VECTOR_DB_PATH
        
        db_path = Path(VECTOR_DB_PATH)
        
        if not db_path.exists():
            print(f"⚠ Database directory does not exist: {VECTOR_DB_PATH}")
            return True
        
        print(f"Deleting database directory: {VECTOR_DB_PATH}")
        shutil.rmtree(db_path)
        print("✓ Database directory deleted successfully")
        # Note: Directory will be recreated automatically by get_vectorstore() when needed
        
        return True
    except ImportError as e:
        print(f"❌ Error: Missing required package: {e}")
        return False
    except Exception as e:
        print(f"❌ Error deleting directory: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Clear ChromaDB data (cache, collection, and optionally directory)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python clear_chroma_db.py           # Clear cache and collection only (recommended)
  python clear_chroma_db.py --full    # Also delete entire database directory
        """
    )
    
    parser.add_argument(
        "--full",
        action="store_true",
        help="Also delete entire database directory (more thorough, but slower)"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompt"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("ChromaDB Data Clearing Script")
    print("=" * 60)
    print()
    
    # Confirmation prompt
    if not args.force:
        action = "clear cache, collection, and delete the database directory" if args.full else "clear cache and collection"
        response = input(f"Are you sure you want to {action}? (yes/no): ").strip().lower()
        
        if response not in ["yes", "y"]:
            print("Operation cancelled.")
            sys.exit(0)
        print()
    
    # Always clear collection and cache
    success = True
    
    # Step 1: Clear collection (while we have a valid connection)
    if not clear_collection():
        success = False
    print()
    
    # Step 2: Clear cache (reset global instance)
    if not clear_cache():
        success = False
    print()
    
    # Step 3: Optionally delete directory
    if args.full:
        if not delete_directory():
            success = False
        print()
    
    print("=" * 60)
    if success:
        print("✓ ChromaDB cleared successfully!")
        print("Note: Collection and directory will be recreated automatically")
        print("      by get_vectorstore() when needed.")
    else:
        print("❌ Failed to clear ChromaDB")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()

