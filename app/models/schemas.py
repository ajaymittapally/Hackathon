from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ConversationStatus(str, Enum):
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    INQUIRING = "inquiring"

class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    preferences: Optional[List[str]] = []
    phone: Optional[str] = None
    role: Optional[str] = None

class UserUpdate(UserCreate):
    user_id: str

class User(UserCreate):
    user_id: str
    created_at: datetime
    updated_at: datetime
    conversation_count: int = 0

class ChatResponse(BaseModel):
    response: str
    tags: Optional[List[str]] = []
    session_id: str
    conversation_id: str
    response_time_ms: int
    context_used: Optional[List[str]] = []

class Conversation(BaseModel):
    conversation_id: str
    user_id: str
    session_id: str
    messages: List[Dict[str, Any]]
    status: ConversationStatus
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    summary: Optional[str] = None

class DocumentUpload(BaseModel):
    filename: str
    content_type: str
    size: int
    processed: bool = False
    chunks: Optional[List[str]] = []

class CalendarEvent(BaseModel):
    event_id: str
    user_id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    attendees: Optional[List[str]] = []
    created_at: datetime

class ResetRequest(BaseModel):
    user_id: Optional[str] = None  # If None, reset all memory
    session_id: Optional[str] = None
