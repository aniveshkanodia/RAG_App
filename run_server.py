#!/usr/bin/env python3
"""
Main entry point for running the RAG API server.

This script ensures proper Python path setup and runs the FastAPI application.

Usage:
    python run_server.py
    OR
    uvicorn api_server:app --reload
"""

import sys
from pathlib import Path

# Ensure project root is in Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import settings (app will be loaded by uvicorn via import string)
from backend.config.settings import API_HOST, API_PORT, API_RELOAD

if __name__ == "__main__":
    import uvicorn
    # Use import string format to enable reload functionality
    uvicorn.run(
        "backend.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_RELOAD
    )

