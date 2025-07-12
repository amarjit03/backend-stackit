from beanie import Document
from pydantic import Field
from datetime import datetime
import uuid

class Vote(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: str = Field(..., index=True)
    answer_id: str = Field(..., index=True)
    value: int = Field(...)  # 1 for upvote, -1 for downvote
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "votes"
        indexes = [
            "user_id",
            "answer_id",
            ("user_id", "answer_id"),  # Compound index to ensure one vote per user per answer
        ]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def __repr__(self):
        return f"<Vote(id={self.id}, user_id={self.user_id}, answer_id={self.answer_id}, value={self.value})>"

