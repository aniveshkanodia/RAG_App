"""
FastAPI backend for RAG Application
Exposes RAG pipeline as REST API
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import tempfile
import shutil

# Import RAG functions from rag_docling
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag_docling import (
    init_rag,
    run_pipeline,
    answer_question,
    process_and_index_file
)

app = FastAPI(title="RAG API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG on startup
@app.on_event("startup")
async def startup_event():
    init_rag()


# Request/Response models
class ChatRequest(BaseModel):
    message: str


class Source(BaseModel):
    page: Optional[int] = None
    section: Optional[str] = None
    source: str
    preview: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source] = []


class UploadResponse(BaseModel):
    message: str
    chunks_count: int


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message and return RAG response with sources
    """
    try:
        # Run RAG pipeline
        response = run_pipeline(request.message)
        
        # Extract answer
        answer = response.get("answer", "")
        
        # Extract and format sources
        sources = []
        context_docs = response.get("context", [])
        
        for doc in context_docs:
            source = Source(
                source=doc.metadata.get("source", "Unknown"),
                preview=doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            )
            
            # Extract page number and section from metadata
            metadata = doc.metadata
            if "dl_meta" in metadata:
                import json
                try:
                    dl_meta = json.loads(metadata["dl_meta"]) if isinstance(metadata["dl_meta"], str) else metadata["dl_meta"]
                    
                    # Extract page number
                    if "doc_items" in dl_meta:
                        for item in dl_meta["doc_items"]:
                            provs = item.get("prov", [])
                            if provs and "page_no" in provs[0]:
                                source.page = provs[0]["page_no"]
                                break
                    
                    # Extract section/headings
                    if "headings" in dl_meta and dl_meta["headings"]:
                        source.section = ", ".join(dl_meta["headings"])
                except (json.JSONDecodeError, TypeError):
                    pass
            
            sources.append(source)
        
        return ChatResponse(answer=answer, sources=sources)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and index a document
    """
    # Validate file type
    allowed_extensions = [".pdf", ".txt", ".docx", ".doc"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not supported. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Save uploaded file to temporary location
    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, file.filename)
    
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process and index the file
        result = process_and_index_file(temp_file_path)
        
        # Extract chunk count from result message
        chunks_count = 0
        if "chunks" in result.lower():
            try:
                chunks_count = int(result.split("chunks")[0].split()[-1])
            except:
                pass
        
        return UploadResponse(
            message=result,
            chunks_count=chunks_count
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

