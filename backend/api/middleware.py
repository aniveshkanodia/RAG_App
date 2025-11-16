"""
API middleware configuration (CORS, etc.).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config.settings import CORS_ORIGINS, CORS_CREDENTIALS


def setup_cors(app: FastAPI) -> None:
    """Configure CORS middleware for the FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=CORS_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

