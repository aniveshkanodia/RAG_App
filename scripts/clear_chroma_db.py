#!/usr/bin/env python3
"""
Standalone script to clear all data from ChromaDB and optionally Supabase.

This script:
1. Resets the global vectorstore cache
2. Deletes the existing ChromaDB collection
3. Optionally (with --full): deletes the entire ChromaDB directory AND clears Supabase registry

Note: The collection and directory are NOT recreated. They will be automatically
created by get_vectorstore() when needed.

Usage:
    python clear_chroma_db.py           # Clear cache and collection only
    python clear_chroma_db.py --full    # Also delete database directory and clear Supabase
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from dotenv import load_dotenv  # Import load_dotenv

# Ensure project root is in Python path before importing backend modules
# Script is in scripts/ directory, so project root is parent.parent
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load environment variables from .env file
load_dotenv(project_root / ".env")


def clear_cache():
    """Reset the global vectorstore cache instance."""
    try:
        from backend.core.vectorstore import reset_vectorstore
        
        print("Resetting vectorstore cache...")
        reset_vectorstore()
        print("✓ Cache cleared successfully")
        return True
    except ModuleNotFoundError as e:
        if "backend" in str(e):
            print(f"❌ Error: Cannot find backend module: {e}")
            print("Make sure you're running this script from the project root or that the project root is in PYTHONPATH")
        else:
            print(f"❌ Error: Missing required package: {e}")
            print("Please install required packages: pip install langchain-chroma langchain-ollama")
        return False
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
        
    except ModuleNotFoundError as e:
        if "backend" in str(e):
            print(f"❌ Error: Cannot find backend module: {e}")
            print("Make sure you're running this script from the project root or that the project root is in PYTHONPATH")
        else:
            print(f"❌ Error: Missing required package: {e}")
            print("Please install required packages: pip install langchain-chroma langchain-ollama")
        return False
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
    except ModuleNotFoundError as e:
        if "backend" in str(e):
            print(f"❌ Error: Cannot find backend module: {e}")
            print("Make sure you're running this script from the project root or that the project root is in PYTHONPATH")
        else:
            print(f"❌ Error: Missing required package: {e}")
        return False
    except ImportError as e:
        print(f"❌ Error: Missing required package: {e}")
        return False
    except Exception as e:
        print(f"❌ Error deleting directory: {e}")
        return False


def clear_supabase():
    """Clear all documents from Supabase registry."""
    try:
        from backend.utils.document_registry import get_supabase_client
        
        # --- ADDED VALIDATION ---
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")  # Changed from SUPABASE_KEY to SUPABASE_ANON_KEY
        
        if not url:
            print("❌ Error: SUPABASE_URL is not set in environment.")
            return False
        if not key:
            print("❌ Error: SUPABASE_ANON_KEY is not set in environment.") # Update error message too
            return False
            
        print(f"Connecting to Supabase at {url[:8]}...")  # Print partial URL to verify
        # ------------------------

        client = get_supabase_client()
        
        print("Deleting all documents from registry...")
        # Delete all documents - use a filter that matches all rows
        # (Supabase requires a filter for DELETE operations)
        # Using .neq("content_hash", "") matches all rows where content_hash is not empty
        # which should be all valid documents (content_hash is required)
        result = client.table("documents").delete().neq("content_hash", "").execute()
        
        # Count deleted documents if available
        # Supabase returns deleted rows in result.data
        deleted_count = len(result.data) if result.data else 0
        if deleted_count > 0:
            print(f"✓ Deleted {deleted_count} document(s) from Supabase registry")
        else:
            # Could be empty table or result.data is None (some Supabase versions)
            # Check if operation succeeded by checking for errors
            print("✓ Supabase registry cleared (table was empty or all documents deleted)")
        return True
        
    except ModuleNotFoundError as e:
        if "backend" in str(e):
            print(f"❌ Error: Cannot find backend module: {e}")
            print("Make sure you're running this script from the project root or that the project root is in PYTHONPATH")
        else:
            print(f"❌ Error: Missing required package: {e}")
        return False
    except ImportError as e:
        print(f"❌ Error: Missing required package: {e}")
        return False
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "row-level security" in error_msg or "policy" in error_msg or "permission denied" in error_msg:
            print(f"❌ Error: Access denied by Row Level Security policy: {e}")
            print("Please ensure RLS policies allow DELETE operations for the anon role.")
        else:
            print(f"❌ Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error clearing Supabase: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Clear ChromaDB data (cache, collection, and optionally directory and Supabase)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python clear_chroma_db.py           # Clear cache and collection only (recommended)
  python clear_chroma_db.py --full    # Also delete database directory and clear Supabase
        """
    )
    
    parser.add_argument(
        "--full",
        action="store_true",
        help="Also delete entire database directory and clear Supabase registry (more thorough, but slower)"
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
        action = "clear cache, collection, delete the database directory, and clear Supabase registry" if args.full else "clear cache and collection"
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
        
        # Step 4: Clear Supabase registry (only with --full)
        if not clear_supabase():
            success = False
        print()
    
    print("=" * 60)
    if success:
        if args.full:
            print("✓ ChromaDB and Supabase cleared successfully!")
        else:
            print("✓ ChromaDB cleared successfully!")
        print("Note: Collection and directory will be recreated automatically")
        print("      by get_vectorstore() when needed.")
    else:
        print("❌ Failed to clear data")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
