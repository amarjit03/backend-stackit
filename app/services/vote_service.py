from typing import Optional
from fastapi import HTTPException, status
from app.models.vote import Vote
from app.models.answer import Answer
from app.schemas.vote import VoteCreate
from app.utils.logger import get_logger

logger = get_logger(__name__)

class VoteService:
    
    @staticmethod
    async def create_or_update_vote(vote_data: VoteCreate, user_id: str) -> Vote:
        """Create or update a vote"""
        # Verify answer exists
        answer = await Answer.get(vote_data.answer_id)
        if not answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found"
            )
        
        # Check if user is trying to vote on their own answer
        if answer.user_id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot vote on your own answer"
            )
        
        # Check if user already voted on this answer
        existing_vote = await Vote.find_one({
            "user_id": user_id,
            "answer_id": vote_data.answer_id
        })
        
        if existing_vote:
            # Update existing vote
            if existing_vote.value == vote_data.value:
                # Same vote, remove it (toggle off)
                await existing_vote.delete()
                logger.info(f"Vote removed: {existing_vote.id}")
                return None
            else:
                # Different vote, update it
                existing_vote.value = vote_data.value
                await existing_vote.save()
                logger.info(f"Vote updated: {existing_vote.id}")
                return existing_vote
        else:
            # Create new vote
            vote = Vote(
                user_id=user_id,
                answer_id=vote_data.answer_id,
                value=vote_data.value
            )
            await vote.insert()
            logger.info(f"Vote created: {vote.id}")
            return vote
    
    @staticmethod
    async def get_vote_stats(answer_id: str, user_id: Optional[str] = None) -> dict:
        """Get vote statistics for an answer"""
        votes = await Vote.find(Vote.answer_id == answer_id).to_list()
        
        upvotes = sum(1 for vote in votes if vote.value == 1)
        downvotes = sum(1 for vote in votes if vote.value == -1)
        total_score = upvotes - downvotes
        
        user_vote = 0
        if user_id:
            user_vote_obj = await Vote.find_one({
                "user_id": user_id,
                "answer_id": answer_id
            })
            if user_vote_obj:
                user_vote = user_vote_obj.value
        
        return {
            "answer_id": answer_id,
            "total_score": total_score,
            "upvotes": upvotes,
            "downvotes": downvotes,
            "user_vote": user_vote
        }
    
    @staticmethod
    async def get_user_vote(user_id: str, answer_id: str) -> Optional[Vote]:
        """Get user's vote for a specific answer"""
        return await Vote.find_one({
            "user_id": user_id,
            "answer_id": answer_id
        })
    
    @staticmethod
    async def remove_vote(user_id: str, answer_id: str) -> bool:
        """Remove user's vote for an answer"""
        vote = await Vote.find_one({
            "user_id": user_id,
            "answer_id": answer_id
        })
        
        if not vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vote not found"
            )
        
        await vote.delete()
        logger.info(f"Vote removed: {vote.id}")
        return True

