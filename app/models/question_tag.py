from beanie import Document
from pydantic import Field
import uuid

class QuestionTag(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    question_id: str = Field(..., index=True)
    tag_id: str = Field(..., index=True)
    
    class Settings:
        name = "question_tags"
        indexes = [
            "question_id",
            "tag_id",
            ("question_id", "tag_id"),  # Compound index to ensure uniqueness
        ]
    
    def __repr__(self):
        return f"<QuestionTag(id={self.id}, question_id={self.question_id}, tag_id={self.tag_id})>"

