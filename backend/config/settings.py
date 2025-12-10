"""
Application settings and configuration management.
Centralizes all configuration from environment variables and constants.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set tokenizer parallelism to avoid warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"

# CORS Configuration
# SECURITY: Never use "*" in production - specify exact origins
# Default to localhost for development, but require explicit setting for production
_cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:3000")
CORS_ORIGINS = _cors_origins_env.split(",") if _cors_origins_env else []
CORS_CREDENTIALS = os.getenv("CORS_CREDENTIALS", "false").lower() == "true"

# Logging Configuration
RAG_LOG_PATH = os.getenv("RAG_LOG_PATH", "logs/rag_turns.jsonl")

# LangSmith Configuration (for tracing)
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT", "")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "")

