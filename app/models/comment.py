from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
import uuid

class Comment(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: str = Field(..., index=True)
    answer_id: str = Field(..., index=True)
    parent_id: Optional[str] = Field(default=None, index=True)  # For nested comments
    text: str = Field(...)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "comments"
        indexes = [
            "user_id",
            "answer_id",
            "parent_id",
            "created_at",
        ]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def __repr__(self):
        return f"<Comment(id={self.id}, user_id={self.user_id}, answer_id={self.answer_id})>"

