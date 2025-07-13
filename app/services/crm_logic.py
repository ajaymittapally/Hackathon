from datetime import datetime
from bson.objectid import ObjectId
from app.models.schemas import UserCreate, UserUpdate
from app.database.database import users_collection

def create_user(user: UserCreate):
    user_dict = user.dict()
    user_dict["conversations"] = []
    user_dict["created_at"] = datetime.utcnow()
    user_id = users_collection.insert_one(user_dict).inserted_id
    return {"user_id": str(user_id)}

def update_user(user: UserUpdate):
    users_collection.update_one({"_id": ObjectId(user.user_id)}, {"$set": user.dict(exclude={"user_id"})})
    return {"message": "User updated"}

def delete_user(user_id: str) -> bool:
    """Delete a user and all their associated data"""
    try:
        result = users_collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False


def save_conversation(user_id: str, session_id: str, message: str, response: str, tags: list[str]) -> str:
    conversation_id = str(ObjectId())
    entry = {
        "conversation_id": conversation_id,
        "session_id": session_id,
        "message": message,
        "response": response,
        "tags": tags,
        "timestamp": datetime.utcnow()
    }
    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"conversations": entry}}
    )
    return conversation_id


def get_conversations(user_id: str):
    user = users_collection.find_one({"_id": ObjectId(user_id)}, {"conversations": 1})
    return user.get("conversations", []) if user else []


def get_user(user_id: str):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        user["user_id"] = str(user["_id"])
        user.pop("_id", None)
        return user
    return None

def get_conversation_history_for_context(user_id: str, limit: int = 5) -> str:
    user = users_collection.find_one({"_id": ObjectId(user_id)}, {"conversations": 1})
    if not user or "conversations" not in user:
        return ""
    history = user["conversations"][-limit:]
    return "\n".join([f"User: {conv['message']}\nBot: {conv['response']}" for conv in history])
