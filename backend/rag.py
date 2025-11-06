"""
RAG pipeline module.
Contains functions for initializing and running the RAG pipeline.
"""

from dotenv import load_dotenv

# Load environment variables from a .env file for langsmith tracing
load_dotenv()

import os
import json
from typing import Dict, Any

# Set tokenizer parallelism to avoid warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langsmith import traceable

# Global variables
embeddings = None
vectordb = None
retriever = None
llm = None
rag_chain = None
PROMPT = None
TOP_K = 4


def init_rag():
    """Initialize the RAG pipeline components."""
    global embeddings, vectordb, retriever, llm, rag_chain, PROMPT
    
    if rag_chain is not None:
        return
    
    # Initialize embeddings
    embeddings = OllamaEmbeddings(model="qwen3-embedding:0.6b")
    
    # Initialize vector database
    vectordb = Chroma(
        collection_name="documents",
        embedding_function=embeddings,
        persist_directory="./db/chroma_db",
    )
    
    # Initialize retriever
    retriever = vectordb.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K},
    )
    
    # Initialize LLM
    llm = ChatOllama(model="qwen3:0.6b", keep_alive="2h", temperature=0)
    
    # Define prompt template (following langchain-docling example pattern)
    PROMPT = PromptTemplate.from_template(
        "Context information is below.\n"
        "---------------------\n"
        "{context}\n"
        "---------------------\n"
        "Given the context information and not prior knowledge, answer the query.\n"
        "Query: {input}\n"
        "Answer:\n"
    )
    
    # Build RAG pipeline using langchain_core.runnables
    # Step 1: Wrap document retrieval
    retrieve_docs = RunnableLambda(
        lambda input_dict: {
            "docs": retriever.invoke(input_dict["input"]),
            "question": input_dict["input"]
        }
    )
    
    # Step 2: Format prompt with context and question
    prompt_step = RunnableLambda(
        lambda input_dict: {
            "input": input_dict["question"],
            "context": "\n\n".join(doc.page_content for doc in input_dict["docs"]),
            "docs": input_dict["docs"]
        }
    )
    
    # Step 3: Get LLM response and format final response
    def call_llm_and_format(input_dict):
        """Call LLM and return structured response with answer and context."""
        formatted_prompt = PROMPT.format(
            context=input_dict["context"],
            input=input_dict["input"]
        )
        llm_response = llm.invoke(formatted_prompt)
        answer = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
        return {
            "answer": answer,
            "context": input_dict["docs"],
            "input": input_dict["input"]
        }
    
    llm_step = RunnableLambda(call_llm_and_format)
    
    # Build the complete pipeline
    rag_chain = retrieve_docs | prompt_step | llm_step


@traceable(name="RAGApp_v2")
def run_pipeline(question: str) -> Dict[str, Any]:
    """Run the RAG pipeline and return structured response with sources.
    
    Args:
        question: User question
        
    Returns:
        Dictionary with 'answer', 'context', and 'input' keys
    """
    global rag_chain
    
    init_rag()
    
    if rag_chain is None:
        raise RuntimeError("RAG chain not initialized")
    
    # Invoke the chain (following langchain-docling example pattern)
    response = rag_chain.invoke({"input": question})
    return response


def answer_question(question: str) -> str:
    """Answer a question using the RAG pipeline with source attribution.
    
    Args:
        question: User question
        
    Returns:
        Answer string with source information
    """
    response = run_pipeline(question)
    answer = response["answer"]
    
    # Always include sources
    sources_info = []
    for i, doc in enumerate(response.get("context", []), 1):
        source_info = f"\n\nSource {i}:"
        
        metadata = doc.metadata
        if metadata:
            # Deserialize JSON metadata if present (we stored dl_meta as JSON string)
            dl_meta = {}
            if "dl_meta" in metadata:
                dl_meta_value = metadata["dl_meta"]
                if isinstance(dl_meta_value, str):
                    try:
                        dl_meta = json.loads(dl_meta_value)
                    except (json.JSONDecodeError, TypeError):
                        dl_meta = {}
                elif isinstance(dl_meta_value, dict):
                    dl_meta = dl_meta_value
            
            # Add headings if available (from docling metadata)
            if "headings" in dl_meta:
                headings = dl_meta["headings"]
                if headings:
                    source_info += f"\n  Section: {', '.join(headings)}"
            
            # Add page number if available (simplified extraction)
            if "doc_items" in dl_meta:
                for item in dl_meta["doc_items"]:
                    provs = item.get("prov", [])
                    if provs and "page_no" in provs[0]:
                        source_info += f"\n  Page: {provs[0]['page_no']}"
                        break
            
            # Add source file/path
            if "source" in metadata:
                source_info += f"\n  Source: {metadata['source']}"
        
        # Add preview of content
        preview = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
        source_info += f"\n  Preview: {preview}"
        
        sources_info.append(source_info)
    
    if sources_info:
        answer += "\n\n--- Sources ---" + "".join(sources_info)
    
    return answer

