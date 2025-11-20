"""
Prompt template management for RAG pipeline.
"""

from langchain_core.prompts import ChatPromptTemplate
from backend.core.config import SYSTEM_PROMPT

# RAG prompt template with system message
RAG_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", 
     "Context:\n"
     "---------------------\n"
     "{context}\n"
     "---------------------\n"
     "Question: {input}")
])


def format_rag_prompt(context: str, question: str):
    """Format RAG prompt with context and question.
    
    Args:
        context: Retrieved context documents formatted as string
        question: User's question
        
    Returns:
        Formatted prompt messages ready for LLM
    """
    return RAG_PROMPT_TEMPLATE.format_messages(context=context, input=question)

