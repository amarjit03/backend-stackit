from beanie import Document
from pydantic import Field
from typing import List
from datetime import datetime
import uuid

class Question(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: str = Field(..., index=True)
    title: str = Field(..., index=True)
    description: str = Field(...)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "questions"
        indexes = [
            "user_id",
            "title",
            "tags",
            "created_at",
        ]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def __repr__(self):
        return f"<Question(id={self.id}, title={self.title})>"

