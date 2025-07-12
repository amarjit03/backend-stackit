from beanie import Document
from pydantic import Field
from datetime import datetime
import uuid

class Answer(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    question_id: str = Field(..., index=True)
    user_id: str = Field(..., index=True)
    description: str = Field(...)
    is_accepted: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "answers"
        indexes = [
            "question_id",
            "user_id",
            "is_accepted",
            "created_at",
        ]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def __repr__(self):
        return f"<Answer(id={self.id}, question_id={self.question_id})>"

