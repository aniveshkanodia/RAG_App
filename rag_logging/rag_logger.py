"""
RAG turn logging module.
Logs each RAG turn to a JSONL file for offline evaluation.
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

# Configure standard logging
logger = logging.getLogger(__name__)

# Default log file path
DEFAULT_LOG_PATH = "logs/rag_turns.jsonl"


class RagTurnLogRecord(BaseModel):
    """Pydantic model for RAG turn log record."""
    timestamp: str = Field(..., description="ISO format timestamp")
    conversation_id: str = Field(..., description="Unique conversation identifier")
    turn_index: int = Field(..., description="Turn index within conversation (0, 1, 2...)")
    user_query: str = Field(..., description="User's question")
    answer: str = Field(..., description="Generated answer")
    contexts: List[str] = Field(..., description="List of retrieved chunk texts")
    chunking_strategy: str = Field(..., description="Chunking strategy identifier")


def get_log_path() -> str:
    """Get log file path from environment variable or use default.
    
    Returns:
        Path to the log file
    """
    return os.getenv("RAG_LOG_PATH", DEFAULT_LOG_PATH)


def ensure_log_directory(log_path: str) -> None:
    """Ensure the log directory exists.
    
    Args:
        log_path: Path to the log file
    """
    log_dir = os.path.dirname(log_path)
    if log_dir and not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to create log directory {log_dir}: {e}")


def log_rag_turn(record: RagTurnLogRecord) -> None:
    """Log a RAG turn to JSONL file.
    
    This function is non-blocking and failure-tolerant. If logging fails,
    it logs an error but does not raise an exception.
    
    Args:
        record: RAG turn log record to write
    """
    try:
        log_path = get_log_path()
        ensure_log_directory(log_path)
        
        # Convert record to dict and serialize to JSON
        record_dict = record.model_dump()
        json_line = json.dumps(record_dict, ensure_ascii=False)
        
        # Append to log file (append mode)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json_line + "\n")
            
    except Exception as e:
        # Log error but don't raise - logging failures should not break requests
        logger.error(f"Failed to log RAG turn: {e}", exc_info=True)


def create_log_record(
    conversation_id: str,
    turn_index: int,
    user_query: str,
    answer: str,
    contexts: List[str],
    chunking_strategy: str,
    timestamp: Optional[str] = None
) -> RagTurnLogRecord:
    """Create a RAG turn log record.
    
    Args:
        conversation_id: Unique conversation identifier
        turn_index: Turn index within conversation
        user_query: User's question
        answer: Generated answer
        contexts: List of retrieved chunk texts
        chunking_strategy: Chunking strategy identifier
        timestamp: Optional ISO format timestamp (defaults to current time)
        
    Returns:
        RagTurnLogRecord instance
    """
    if timestamp is None:
        timestamp = datetime.utcnow().isoformat() + "Z"
    
    return RagTurnLogRecord(
        timestamp=timestamp,
        conversation_id=conversation_id,
        turn_index=turn_index,
        user_query=user_query,
        answer=answer,
        contexts=contexts,
        chunking_strategy=chunking_strategy
    )

