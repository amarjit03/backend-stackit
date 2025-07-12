from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class MCQQuestionBase(BaseModel):
    question_text: str = Field(..., min_length=10)
    option_a: str = Field(..., min_length=1)
    option_b: str = Field(..., min_length=1)
    option_c: str = Field(..., min_length=1)
    option_d: str = Field(..., min_length=1)
    correct_option: str = Field(..., pattern="^[ABCD]$")

class MCQQuestionCreate(MCQQuestionBase):
    quiz_id: str

class MCQQuestionResponse(MCQQuestionBase):
    id: str
    quiz_id: str
    
    class Config:
        from_attributes = True

class MCQQuestionForQuiz(BaseModel):
    """MCQ Question without correct answer (for taking quiz)"""
    id: str
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str

class MCQQuizBase(BaseModel):
    topic: str = Field(..., min_length=1, max_length=100)

class MCQQuizCreate(MCQQuizBase):
    pass

class MCQQuizResponse(MCQQuizBase):
    id: str
    user_id: str
    score: int
    total_questions: int
    completed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class QuizAnswer(BaseModel):
    question_id: str
    selected_option: str = Field(..., pattern="^[ABCD]$")

class QuizSubmission(BaseModel):
    quiz_id: str
    answers: List[QuizAnswer]

class QuizResult(BaseModel):
    quiz_id: str
    score: int
    total_questions: int
    percentage: float
    correct_answers: List[str]
    user_answers: List[QuizAnswer]
    passed: bool  # True if score >= 70%

class TopicStats(BaseModel):
    topic: str
    total_quizzes: int
    average_score: float
    best_score: int
    completion_rate: float

