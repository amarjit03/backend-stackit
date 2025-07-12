from pydantic import BaseModel, Field
from datetime import datetime

class VoteBase(BaseModel):
    answer_id: str
    value: int = Field(..., ge=-1, le=1)  # -1 for downvote, 1 for upvote

class VoteCreate(VoteBase):
    pass

class VoteResponse(VoteBase):
    id: str
    user_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class VoteStats(BaseModel):
    answer_id: str
    total_score: int
    upvotes: int
    downvotes: int
    user_vote: int = 0  # Current user's vote if any

