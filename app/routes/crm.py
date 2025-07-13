from fastapi import APIRouter, HTTPException
from app.models.schemas import UserCreate, UserUpdate
from app.services.crm_logic import create_user, update_user, get_conversations, get_user, delete_user

router = APIRouter()

@router.post("/create_user")
def create(user: UserCreate):
    """Create a new user in the CRM system"""
    try:
        result = create_user(user)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

@router.put("/update_user")
def update(user: UserUpdate):
    """Update an existing user"""
    try:
        result = update_user(user)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")

@router.get("/conversations/{user_id}")
def get_history(user_id: str):
    """Get conversation history for a user"""
    try:
        conversations = get_conversations(user_id)
        return {
            "user_id": user_id,
            "conversations": conversations,
            "total_conversations": len(conversations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversations: {str(e)}")

@router.get("/user/{user_id}")
def get_user_info(user_id: str):
    """Get user information"""
    try:
        user = get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")

@router.delete("/user/{user_id}")
def delete_user_route(user_id: str):
    """Delete a user and all associated data"""
    try:
        success = delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")
