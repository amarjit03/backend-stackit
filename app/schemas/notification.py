from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.notification import NotificationType

class NotificationBase(BaseModel):
    type: NotificationType
    content: str = Field(..., min_length=1, max_length=500)
    question_id: Optional[str] = None

class NotificationCreate(NotificationBase):
    user_id: str

class NotificationResponse(NotificationBase):
    id: str
    user_id: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class NotificationUpdate(BaseModel):
    is_read: bool

class NotificationStats(BaseModel):
    total_count: int
    unread_count: int
    recent_count: int  # Last 24 hours

