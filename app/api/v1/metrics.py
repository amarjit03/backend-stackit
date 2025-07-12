from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from app.schemas.metrics import (
    UserMetrics, PopularUser, QuestionMetrics, PopularQuestion,
    EngagementStats, UserActivity
)
from app.services.metrics_service import MetricsService
from app.core.auth import get_current_active_user
from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/metrics", tags=["Metrics & Analytics"])

@router.get("/users/popular", response_model=List[PopularUser])
async def get_popular_users(
    limit: int = Query(20, ge=1, le=100)
):
    """Get most popular users by reputation score"""
    try:
        popular_users = await MetricsService.get_popular_users(limit)
        return popular_users
    except Exception as e:
        logger.error(f"Get popular users error: {e}")
        raise

@router.get("/users/active", response_model=List[UserActivity])
async def get_most_active_users(
    limit: int = Query(20, ge=1, le=100)
):
    """Get most active users this week"""
    try:
        active_users = await MetricsService.get_most_active_users(limit)
        return active_users
    except Exception as e:
        logger.error(f"Get active users error: {e}")
        raise

@router.get("/users/{user_id}", response_model=UserMetrics)
async def get_user_metrics(user_id: str):
    """Get comprehensive metrics for a specific user"""
    try:
        metrics = await MetricsService.get_user_metrics(user_id)
        if not metrics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return metrics
    except Exception as e:
        logger.error(f"Get user metrics error: {e}")
        raise

@router.get("/users/{user_id}/activity", response_model=UserActivity)
async def get_user_activity(user_id: str):
    """Get user activity for the current week"""
    try:
        activity = await MetricsService.get_user_activity(user_id)
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return activity
    except Exception as e:
        logger.error(f"Get user activity error: {e}")
        raise

@router.get("/questions/popular", response_model=List[PopularQuestion])
async def get_popular_questions(
    limit: int = Query(20, ge=1, le=100),
    period: str = Query("all", regex="^(all|week|month)$")
):
    """Get most popular questions by engagement score"""
    try:
        popular_questions = await MetricsService.get_popular_questions(limit, period)
        return popular_questions
    except Exception as e:
        logger.error(f"Get popular questions error: {e}")
        raise

@router.get("/questions/top", response_model=List[PopularQuestion])
async def get_top_questions(
    limit: int = Query(20, ge=1, le=100)
):
    """Get top questions by vote score (all time)"""
    try:
        top_questions = await MetricsService.get_top_questions(limit)
        return top_questions
    except Exception as e:
        logger.error(f"Get top questions error: {e}")
        raise

@router.get("/questions/trending", response_model=List[PopularQuestion])
async def get_trending_questions(
    limit: int = Query(20, ge=1, le=100)
):
    """Get trending questions from the last week"""
    try:
        trending_questions = await MetricsService.get_trending_questions(limit)
        return trending_questions
    except Exception as e:
        logger.error(f"Get trending questions error: {e}")
        raise

@router.get("/questions/{question_id}", response_model=QuestionMetrics)
async def get_question_metrics(question_id: str):
    """Get comprehensive metrics for a specific question"""
    try:
        metrics = await MetricsService.get_question_metrics(question_id)
        if not metrics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        return metrics
    except Exception as e:
        logger.error(f"Get question metrics error: {e}")
        raise

@router.get("/engagement", response_model=EngagementStats)
async def get_engagement_stats():
    """Get overall platform engagement statistics"""
    try:
        stats = await MetricsService.get_engagement_stats()
        return stats
    except Exception as e:
        logger.error(f"Get engagement stats error: {e}")
        raise

@router.get("/my-metrics", response_model=UserMetrics)
async def get_my_metrics(
    current_user: User = Depends(get_current_active_user)
):
    """Get metrics for the current authenticated user"""
    try:
        metrics = await MetricsService.get_user_metrics(current_user.id)
        return metrics
    except Exception as e:
        logger.error(f"Get my metrics error: {e}")
        raise

@router.get("/my-activity", response_model=UserActivity)
async def get_my_activity(
    current_user: User = Depends(get_current_active_user)
):
    """Get activity for the current authenticated user"""
    try:
        activity = await MetricsService.get_user_activity(current_user.id)
        return activity
    except Exception as e:
        logger.error(f"Get my activity error: {e}")
        raise

@router.get("/leaderboard/reputation", response_model=List[PopularUser])
async def get_reputation_leaderboard(
    limit: int = Query(50, ge=1, le=100)
):
    """Get reputation leaderboard (top users by reputation)"""
    try:
        leaderboard = await MetricsService.get_popular_users(limit)
        return leaderboard
    except Exception as e:
        logger.error(f"Get reputation leaderboard error: {e}")
        raise

@router.get("/leaderboard/activity", response_model=List[UserActivity])
async def get_activity_leaderboard(
    limit: int = Query(50, ge=1, le=100)
):
    """Get activity leaderboard (most active users this week)"""
    try:
        leaderboard = await MetricsService.get_most_active_users(limit)
        return leaderboard
    except Exception as e:
        logger.error(f"Get activity leaderboard error: {e}")
        raise

