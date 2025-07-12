from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from app.schemas.vote import VoteCreate, VoteResponse, VoteStats
from app.services.vote_service import VoteService
from app.core.auth import get_current_active_user
from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/votes", tags=["Votes"])

@router.post("/", response_model=Optional[VoteResponse])
async def vote_answer(
    vote_data: VoteCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Vote on an answer (upvote/downvote)"""
    try:
        vote = await VoteService.create_or_update_vote(vote_data, current_user.id)
        return vote
    except Exception as e:
        logger.error(f"Vote error: {e}")
        raise

@router.get("/answer/{answer_id}/stats", response_model=VoteStats)
async def get_vote_stats(
    answer_id: str,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """Get vote statistics for an answer"""
    try:
        user_id = current_user.id if current_user else None
        stats = await VoteService.get_vote_stats(answer_id, user_id)
        return stats
    except Exception as e:
        logger.error(f"Get vote stats error: {e}")
        raise

@router.get("/answer/{answer_id}/my-vote", response_model=Optional[VoteResponse])
async def get_my_vote(
    answer_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's vote for an answer"""
    try:
        vote = await VoteService.get_user_vote(current_user.id, answer_id)
        return vote
    except Exception as e:
        logger.error(f"Get user vote error: {e}")
        raise

@router.delete("/answer/{answer_id}")
async def remove_vote(
    answer_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Remove vote from an answer"""
    try:
        await VoteService.remove_vote(current_user.id, answer_id)
        return {"message": "Vote removed successfully"}
    except Exception as e:
        logger.error(f"Remove vote error: {e}")
        raise

