from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import List, Optional
from app.services.calendar_service import calendar_service

router = APIRouter()

@router.post("/events")
def create_event(user_id: str, title: str, description: Optional[str] = None,
                start_time: Optional[datetime] = None, end_time: Optional[datetime] = None,
                location: Optional[str] = None, attendees: Optional[List[str]] = None):
    """Create a new calendar event"""
    try:
        result = calendar_service.create_event(
            user_id=user_id,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            location=location,
            attendees=attendees
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")

@router.get("/events/{user_id}")
def get_events(user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
    """Get events for a user"""
    try:
        events = calendar_service.get_user_events(user_id, start_date, end_date)
        return {
            "user_id": user_id,
            "events": events,
            "total_events": len(events)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get events: {str(e)}")

@router.put("/events/{event_id}")
def update_event(event_id: str, **kwargs):
    """Update an existing event"""
    try:
        result = calendar_service.update_event(event_id, **kwargs)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update event: {str(e)}")

@router.delete("/events/{event_id}")
def delete_event(event_id: str):
    """Delete an event"""
    try:
        result = calendar_service.delete_event(event_id)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete event: {str(e)}")

@router.get("/suggestions/{user_id}")
def get_meeting_suggestions(user_id: str, duration_minutes: int = 60, 
                          preferred_days: Optional[List[str]] = None):
    """Get meeting time suggestions"""
    try:
        suggestions = calendar_service.suggest_meeting_time(user_id, duration_minutes, preferred_days)
        return {
            "user_id": user_id,
            "duration_minutes": duration_minutes,
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}") 