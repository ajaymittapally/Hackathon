from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.services.chatbot import get_chat_response

router = APIRouter()

@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Enhanced chat endpoint with session management and CRM integration"""
    try:
        response = get_chat_response(
            user_id=request.user_id, 
            message=request.message,
            session_id=request.session_id
        )
        return ChatResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
