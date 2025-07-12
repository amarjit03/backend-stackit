from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from app.schemas.mcq import (
    MCQQuizCreate, MCQQuizResponse, MCQQuestionForQuiz,
    QuizSubmission, QuizResult, TopicStats
)
from app.services.mcq_service import MCQService
from app.core.auth import get_current_active_user
from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/mcq", tags=["MCQ Quiz"])

@router.post("/quiz", response_model=MCQQuizResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    quiz_data: MCQQuizCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new MCQ quiz"""
    try:
        quiz = await MCQService.create_quiz(quiz_data, current_user.id)
        return quiz
    except Exception as e:
        logger.error(f"Quiz creation error: {e}")
        raise

@router.get("/quiz/{quiz_id}", response_model=MCQQuizResponse)
async def get_quiz(
    quiz_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get quiz details"""
    quiz = await MCQService.get_quiz_by_id(quiz_id)
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    if quiz.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this quiz"
        )
    
    return quiz

@router.get("/quiz/{quiz_id}/questions", response_model=List[MCQQuestionForQuiz])
async def get_quiz_questions(
    quiz_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get questions for a quiz (without correct answers)"""
    quiz = await MCQService.get_quiz_by_id(quiz_id)
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    if quiz.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this quiz"
        )
    
    if quiz.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz already completed"
        )
    
    try:
        questions = await MCQService.get_quiz_questions(quiz_id)
        return questions
    except Exception as e:
        logger.error(f"Get quiz questions error: {e}")
        raise

@router.post("/quiz/submit", response_model=QuizResult)
async def submit_quiz(
    submission: QuizSubmission,
    current_user: User = Depends(get_current_active_user)
):
    """Submit quiz answers"""
    try:
        result = await MCQService.submit_quiz(submission, current_user.id)
        return result
    except Exception as e:
        logger.error(f"Quiz submission error: {e}")
        raise

@router.get("/my-quizzes", response_model=List[MCQQuizResponse])
async def get_my_quizzes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's quizzes"""
    try:
        quizzes = await MCQService.get_user_quizzes(
            current_user.id, skip=skip, limit=limit
        )
        return quizzes
    except Exception as e:
        logger.error(f"Get user quizzes error: {e}")
        raise

@router.get("/topics", response_model=List[str])
async def get_available_topics():
    """Get list of available quiz topics"""
    try:
        topics = await MCQService.get_available_topics()
        return topics
    except Exception as e:
        logger.error(f"Get topics error: {e}")
        raise

@router.get("/topics/{topic}/stats", response_model=TopicStats)
async def get_topic_stats(
    topic: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get statistics for a topic"""
    try:
        stats = await MCQService.get_topic_stats(current_user.id, topic)
        return stats
    except Exception as e:
        logger.error(f"Get topic stats error: {e}")
        raise

@router.get("/leaderboard/{topic}")
async def get_topic_leaderboard(
    topic: str,
    limit: int = Query(10, ge=1, le=50)
):
    """Get leaderboard for a topic (top performers)"""
    try:
        # This would require aggregating data across users
        # For now, return a placeholder
        return {"message": "Leaderboard feature coming soon"}
    except Exception as e:
        logger.error(f"Get leaderboard error: {e}")
        raise

