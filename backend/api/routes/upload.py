"""
Upload API route handlers.
"""

import os
import re
import tempfile
from fastapi import HTTPException, UploadFile, File, Form
from typing import Optional
from backend.api.models.upload import UploadResponse
from backend.services.document_service import process_and_index_file


async def handle_upload(
    file: UploadFile = File(...),
    conversation_id: Optional[str] = Form(None)
) -> UploadResponse:
    """File upload endpoint handler that processes and indexes uploaded files.
    
    Args:
        file: Uploaded file (PDF, TXT, DOCX, DOC, XLSX, or XLS)
        conversation_id: Optional conversation ID to associate the file with a chat session
        
    Returns:
        UploadResponse with success message and number of chunks indexed
        
    Raises:
        HTTPException: If file is invalid, unsupported type, or processing fails
    """
    # Validate file is provided
    if not file:
        raise HTTPException(
            status_code=400,
            detail="No file provided"
        )
    
    # Validate file extension
    file_ext = os.path.splitext(file.filename or "")[1].lower()
    supported_extensions = [".pdf", ".txt", ".docx", ".doc", ".xlsx", ".xls"]
    
    if file_ext not in supported_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Supported types: {', '.join(supported_extensions)}"
        )
    
    # Extract original filename at upload time
    original_filename = file.filename
    
    # Create temporary file to save uploaded file
    temp_file_path = None
    try:
        # Read file content
        file_content = await file.read()
        
        if not file_content:
            raise HTTPException(
                status_code=400,
                detail="File is empty"
            )
        
        # Create temporary file with original extension
        # (Necessary for document loaders which require a file path)
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        # Process and index the file (pass original filename from upload)
        result_message = process_and_index_file(
            temp_file_path, 
            conversation_id=conversation_id,
            original_filename=original_filename
        )
        
        # Extract number of chunks from result message if available
        chunks = None
        if "indexed" in result_message.lower():
            # Try to extract chunk count from message like "indexed 5 chunks"
            match = re.search(r'indexed\s+(\d+)\s+chunks?', result_message, re.IGNORECASE)
            if match:
                chunks = int(match.group(1))
        
        # Check if processing was successful
        if result_message.startswith("Error"):
            raise HTTPException(
                status_code=500,
                detail=result_message
            )
        
        return UploadResponse(
            message=result_message,
            chunks=chunks
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception:
                # Ignore errors during cleanup
                pass

