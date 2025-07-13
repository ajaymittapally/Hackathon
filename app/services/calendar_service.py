import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from app.database.database import calendar_events_collection
from app.models.schemas import CalendarEvent

class CalendarService:
    def __init__(self):
        self.collection = calendar_events_collection
    
    def generate_id(self) -> str:
        """Generate a unique ID"""
        return str(uuid.uuid4())
    
    def create_event(self, user_id: str, title: str, description: Optional[str] = None,
                    start_time: Optional[datetime] = None, end_time: Optional[datetime] = None,
                    location: Optional[str] = None, attendees: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a new calendar event"""
        event_id = self.generate_id()
        if not start_time:
            start_time = datetime.now(timezone.utc) + timedelta(hours=1)
        if not end_time:
            end_time = start_time + timedelta(hours=1)
        event = {
            "event_id": event_id,
            "user_id": user_id,
            "title": title,
            "description": description,
            "start_time": start_time,
            "end_time": end_time,
            "location": location,
            "attendees": attendees or [],
            "created_at": datetime.now(timezone.utc)
        }
        try:
            self.collection.insert_one(event)
            return {**event, "message": "Event created successfully"}
        except Exception as e:
            return {"error": f"Failed to create event: {str(e)}"}

    def get_user_events(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        if not start_date:
            start_date = datetime.now(timezone.utc)
        if not end_date:
            end_date = start_date + timedelta(days=30)
        query = {
            "user_id": user_id,
            "start_time": {"$gte": start_date, "$lte": end_date}
        }
        events = list(self.collection.find(query).sort("start_time", 1))
        for event in events:
            event["event_id"] = event.get("event_id", str(event.get("_id")))
            event["attendees"] = event.get("attendees", [])
            event.pop("_id", None)
        return events

    def update_event(self, event_id: str, **kwargs) -> Dict[str, Any]:
        allowed_fields = ['title', 'description', 'start_time', 'end_time', 'location', 'attendees']
        update = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not update:
            return {"error": "No valid fields to update"}
        result = self.collection.update_one({"event_id": event_id}, {"$set": update})
        if result.modified_count > 0:
            return {"message": "Event updated successfully"}
        else:
            return {"error": "Event not found or no changes made"}

    def delete_event(self, event_id: str) -> Dict[str, Any]:
        result = self.collection.delete_one({"event_id": event_id})
        if result.deleted_count > 0:
            return {"message": "Event deleted successfully"}
        else:
            return {"error": "Event not found"}

    def suggest_meeting_time(self, user_id: str, duration_minutes: int = 60, 
                           preferred_days: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        if not preferred_days:
            preferred_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        end_date = datetime.now(timezone.utc) + timedelta(days=14)
        existing_events = self.get_user_events(user_id, datetime.now(timezone.utc), end_date)
        suggestions = []
        current_time = datetime.now(timezone.utc)
        for i in range(10):
            suggestion_time = current_time + timedelta(days=i+1, hours=9)
            day_name = suggestion_time.strftime('%A').lower()
            if day_name in preferred_days:
                end_time = suggestion_time + timedelta(minutes=duration_minutes)
                conflicts = False
                for event in existing_events:
                    event_start = event['start_time']
                    event_end = event['end_time']
                    if (suggestion_time < event_end and end_time > event_start):
                        conflicts = True
                        break
                if not conflicts:
                    suggestions.append({
                        "start_time": suggestion_time.isoformat(),
                        "end_time": end_time.isoformat(),
                        "day": suggestion_time.strftime('%A'),
                        "time": suggestion_time.strftime('%I:%M %p')
                    })
        return suggestions[:5]

# Global calendar service instance
calendar_service = CalendarService() 