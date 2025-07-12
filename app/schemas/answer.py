from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AnswerBase(BaseModel):
    description: str = Field(..., min_length=10)

class AnswerCreate(AnswerBase):
    question_id: str

class AnswerUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=10)

class AnswerResponse(AnswerBase):
    id: str
    question_id: str
    user_id: str
    is_accepted: bool
    created_at: datetime
    updated_at: datetime
    vote_score: Optional[int] = 0
    
    class Config:
        from_attributes = True

class AnswerWithUser(AnswerResponse):
    username: str
    user_email: str

class AcceptAnswerRequest(BaseModel):
    answer_id: str

