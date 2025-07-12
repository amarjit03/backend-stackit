from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class QuestionBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10)
    tags: List[str] = Field(default_factory=list)

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    tags: Optional[List[str]] = None

class QuestionResponse(QuestionBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    answer_count: Optional[int] = 0
    accepted_answer_id: Optional[str] = None
    
    class Config:
        from_attributes = True

class QuestionWithUser(QuestionResponse):
    username: str
    user_email: str

