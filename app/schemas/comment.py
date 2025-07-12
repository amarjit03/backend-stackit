from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CommentBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)

class CommentCreate(CommentBase):
    answer_id: str
    parent_id: Optional[str] = None  # For nested comments

class CommentUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=1, max_length=1000)

class CommentResponse(CommentBase):
    id: str
    user_id: str
    answer_id: str
    parent_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class CommentWithUser(CommentResponse):
    username: str
    user_email: str

class CommentThread(CommentWithUser):
    replies: List['CommentThread'] = []
    reply_count: int = 0

# Update forward reference
CommentThread.model_rebuild()

