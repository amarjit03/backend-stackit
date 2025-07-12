from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserMetrics(BaseModel):
    user_id: str
    username: str
    email: str
    total_questions: int
    total_answers: int
    total_votes_received: int
    total_comments: int
    accepted_answers: int
    reputation_score: int
    join_date: datetime
    last_activity: Optional[datetime] = None

class PopularUser(BaseModel):
    user_id: str
    username: str
    reputation_score: int
    total_questions: int
    total_answers: int
    accepted_answers: int
    total_votes_received: int

class QuestionMetrics(BaseModel):
    question_id: str
    title: str
    user_id: str
    username: str
    view_count: int = 0
    answer_count: int
    vote_score: int
    comment_count: int
    has_accepted_answer: bool
    created_at: datetime
    last_activity: datetime
    tags: List[str]

class PopularQuestion(BaseModel):
    question_id: str
    title: str
    username: str
    view_count: int = 0
    answer_count: int
    vote_score: int
    engagement_score: float  # Calculated metric
    created_at: datetime
    tags: List[str]

class EngagementStats(BaseModel):
    total_users: int
    total_questions: int
    total_answers: int
    total_votes: int
    total_comments: int
    active_users_today: int
    questions_today: int
    answers_today: int

class TrendingTopic(BaseModel):
    tag_name: str
    question_count: int
    recent_activity: int  # Questions in last 7 days
    growth_rate: float  # Percentage growth

class UserActivity(BaseModel):
    user_id: str
    username: str
    questions_this_week: int
    answers_this_week: int
    votes_this_week: int
    comments_this_week: int
    activity_score: float

