"""
Prompt template management for RAG pipeline.
"""

from langchain_core.prompts import PromptTemplate

# RAG prompt template
RAG_PROMPT_TEMPLATE = PromptTemplate.from_template(
    "Context information is below.\n"
    "---------------------\n"
    "{context}\n"
    "---------------------\n"
    "Given the context information and not prior knowledge, answer the query.\n"
    "Query: {input}\n"
    "Answer:\n"
)


def format_rag_prompt(context: str, question: str) -> str:
    """Format RAG prompt with context and question.
    
    Args:
        context: Retrieved context documents formatted as string
        question: User's question
        
    Returns:
        Formatted prompt string ready for LLM
    """
    return RAG_PROMPT_TEMPLATE.format(context=context, input=question)

