from beanie import Document
from pydantic import Field
from datetime import datetime
from enum import Enum
import uuid

class NotificationType(str, Enum):
    ANSWER = "answer"
    COMMENT = "comment"
    MENTION = "mention"
    VOTE = "vote"

class Notification(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: str = Field(..., index=True)
    type: NotificationType = Field(...)
    content: str = Field(...)
    is_read: bool = Field(default=False)
    question_id: str = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "notifications"
        indexes = [
            "user_id",
            "is_read",
            "created_at",
            "question_id",
        ]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type})>"

