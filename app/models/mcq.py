from beanie import Document
from pydantic import Field
from typing import List
from datetime import datetime
import uuid

class MCQQuestion(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    quiz_id: str = Field(..., index=True)
    question_text: str = Field(...)
    option_a: str = Field(...)
    option_b: str = Field(...)
    option_c: str = Field(...)
    option_d: str = Field(...)
    correct_option: str = Field(...)  # 'A', 'B', 'C', or 'D'
    
    class Settings:
        name = "mcq_questions"
        indexes = [
            "quiz_id",
        ]
    
    def __repr__(self):
        return f"<MCQQuestion(id={self.id}, quiz_id={self.quiz_id})>"

class MCQQuiz(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: str = Field(..., index=True)
    topic: str = Field(..., index=True)
    score: int = Field(default=0)
    total_questions: int = Field(default=0)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "mcq_quizzes"
        indexes = [
            "user_id",
            "topic",
            "created_at",
        ]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def __repr__(self):
        return f"<MCQQuiz(id={self.id}, user_id={self.user_id}, topic={self.topic})>"

