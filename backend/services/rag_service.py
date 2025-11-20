"""
RAG service - Main RAG pipeline orchestration.
Coordinates retrieval, prompt formatting, and LLM generation.
"""

import logging
from typing import Dict, Any, Optional, List
from langchain_core.documents import Document
from langsmith import traceable

from backend.core.retriever import retrieve_documents
from backend.core.prompts import format_rag_prompt
from backend.core.llm import get_llm

logger = logging.getLogger(__name__)


@traceable(name="RAGApp_v2")
def run_rag_pipeline(question: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
    """Run the RAG pipeline and return structured response with sources.
    
    This function orchestrates the complete RAG pipeline:
    1. Retrieve relevant documents (with optional conversation filtering)
    2. Format context from retrieved documents
    3. Generate answer using LLM
    4. Return structured response with answer and context
    
    Args:
        question: User question
        conversation_id: Optional conversation ID to filter documents by chat session.
                        If provided, only retrieves documents with matching conversation_id.
        
    Returns:
        Dictionary with 'answer', 'context', and 'input' keys.
        'context' is always a list of Document objects (never None).
    """
    # Step 1: Retrieve documents with optional conversation filtering
    # retrieve_documents guarantees it returns a list (never None)
    logger.info(f"Retrieving documents for question: '{question[:50]}...' with conversation_id: {conversation_id}")
    docs = retrieve_documents(question, conversation_id=conversation_id)
    logger.info(f"Retrieved {len(docs)} documents")
    
    # Step 2: Format context from retrieved documents
    # Documents are already validated in retrieve_documents, but ensure page_content exists
    valid_docs = [doc for doc in docs if doc.page_content]
    logger.info(f"Valid documents with page_content: {len(valid_docs)}")
    
    # Build context string from valid documents
    if valid_docs:
        context = "\n\n".join(doc.page_content for doc in valid_docs)
        logger.info(f"Built context string of length {len(context)} characters from {len(valid_docs)} documents")
    else:
        context = ""
        logger.warning(f"No valid documents found - context will be empty. Question: '{question[:50]}...'")
    
    # Step 3: Generate answer using LLM
    answer = generate_answer(context, question, valid_docs)
    
    # Step 4: Return structured response
    # Always return context as a list (never None) to ensure type consistency
    return {
        "answer": answer,
        "context": valid_docs,  # Always a list, never None
        "input": question
    }


def generate_answer(context: str, question: str, docs: list) -> str:
    """Generate answer from LLM using context.
    
    This function handles the LLM invocation and answer extraction.
    It formats the prompt, invokes the LLM, and extracts the answer.
    
    Args:
        context: Retrieved context documents formatted as string
        question: User's question
        docs: List of retrieved Document objects (for reference)
        
    Returns:
        Generated answer string from LLM
    """
    if not context:
        logger.warning("Context is empty - LLM will not have document context to answer from")
    
    # Format prompt with context and question
    formatted_prompt = format_rag_prompt(context, question)
    
    # Get LLM instance and invoke
    llm = get_llm()
    llm_response = llm.invoke(formatted_prompt)
    
    # Extract answer from response
    answer = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
    
    return answer

