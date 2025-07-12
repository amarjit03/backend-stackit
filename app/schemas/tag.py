from pydantic import BaseModel, Field
from typing import Optional

class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: str
    question_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

class TagStats(BaseModel):
    name: str
    question_count: int
    recent_questions: int  # Questions in last 30 days

