from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.rag import process_document
import os

router = APIRouter()

@router.post("/")
async def upload_docs(file: UploadFile = File(...)):
    """Upload and process documents for RAG system"""
    try:
        # Validate file type
        allowed_types = [
            "application/pdf",
            "text/plain", 
            "text/csv",
            "application/json"
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file.content_type}. Supported types: {', '.join(allowed_types)}"
            )
        
        # Validate filename
        if not file.filename or len(file.filename.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Filename is required"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Validate file size (10MB limit)
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 10MB"
            )
        
        # Process document
        result = await process_document(
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type
        )
        
        # Check if processing failed
        if "error" in result:
            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )
        
        return {
            "status": "success",
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(file_content),
            "result": result
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")
