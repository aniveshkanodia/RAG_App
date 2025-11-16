"""
LLM initialization and management.
"""

from langchain_ollama import ChatOllama
from backend.core.config import LLM_MODEL, LLM_KEEP_ALIVE, LLM_TEMPERATURE

# Global LLM instance
_llm = None


def get_llm() -> ChatOllama:
    """Initialize and return LLM instance.
    
    Uses singleton pattern to ensure only one instance is created.
    
    Returns:
        ChatOllama instance
    """
    global _llm
    
    if _llm is None:
        _llm = ChatOllama(
            model=LLM_MODEL,
            keep_alive=LLM_KEEP_ALIVE,
            temperature=LLM_TEMPERATURE
        )
    
    return _llm


def reset_llm() -> None:
    """Reset the global LLM instance (useful for testing)."""
    global _llm
    _llm = None

