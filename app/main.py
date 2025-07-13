from fastapi import FastAPI, HTTPException
from app.routes import chat, crm, upload, calendar, rag
from app.models.schemas import ResetRequest
from app.database.database import users_collection
from bson.objectid import ObjectId


app = FastAPI(
    title="Multi-Agentic Conversational AI",
    description="A RESTful API for conversational AI with RAG and CRM integration",
    version="1.0.0"
)

# Register routes
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(upload.router, prefix="/upload_docs", tags=["Upload"])
app.include_router(rag.router, prefix="/rag", tags=["RAG"])
app.include_router(crm.router, prefix="/crm", tags=["CRM"])
app.include_router(calendar.router, prefix="/calendar", tags=["Calendar"])

@app.post("/reset")
def reset_memory(request: ResetRequest):
    try:
        if request.user_id and request.session_id:
            users_collection.update_one(
                {"_id": ObjectId(request.user_id)},
                {"$pull": {"conversations": {"session_id": request.session_id}}}
            )
            return {"message": "Session reset"}
        elif request.user_id:
            users_collection.update_one(
                {"_id": ObjectId(request.user_id)},
                {"$set": {"conversations": []}}
            )
            return {"message": "User conversations reset"}
        else:
            users_collection.update_many({}, {"$set": {"conversations": []}})
            return {"message": "All conversations reset"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset error: {str(e)}")


@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Multi-Agentic Conversational AI API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat",
            "upload": "/upload_docs",
            "rag": "/rag",
            "crm": "/crm",
            "calendar": "/calendar",
            "reset": "/reset"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Test MongoDB connection
        from app.database.database import test_connection
        if test_connection():
            return {"status": "healthy", "database": "connected"}
        else:
            raise HTTPException(status_code=500, detail="Database connection failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
