from typing import List, Optional
from fastapi import HTTPException, status
from datetime import datetime
from app.models.answer import Answer
from app.models.question import Question
from app.models.user import User
from app.models.vote import Vote
from app.schemas.answer import AnswerCreate, AnswerUpdate
from app.utils.logger import get_logger

logger = get_logger(__name__)

class AnswerService:
    
    @staticmethod
    async def create_answer(answer_data: AnswerCreate, user_id: str) -> Answer:
        """Create a new answer"""
        # Verify question exists
        question = await Question.get(answer_data.question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        answer = Answer(
            question_id=answer_data.question_id,
            user_id=user_id,
            description=answer_data.description
        )
        
        await answer.insert()
        logger.info(f"Answer created: {answer.id} for question {answer_data.question_id}")
        return answer
    
    @staticmethod
    async def get_answer_by_id(answer_id: str) -> Optional[Answer]:
        """Get answer by ID"""
        return await Answer.get(answer_id)
    
    @staticmethod
    async def get_answers_by_question(
        question_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Answer]:
        """Get answers for a question"""
        answers = await Answer.find(Answer.question_id == question_id)\
            .sort(-Answer.is_accepted, -Answer.created_at)\
            .skip(skip)\
            .limit(limit)\
            .to_list()
        return answers
    
    @staticmethod
    async def get_answers_by_user(user_id: str, skip: int = 0, limit: int = 20) -> List[Answer]:
        """Get answers by user"""
        answers = await Answer.find(Answer.user_id == user_id)\
            .sort(-Answer.created_at)\
            .skip(skip)\
            .limit(limit)\
            .to_list()
        return answers
    
    @staticmethod
    async def update_answer(answer_id: str, answer_data: AnswerUpdate, user_id: str) -> Answer:
        """Update an answer"""
        answer = await Answer.get(answer_id)
        if not answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found"
            )
        
        if answer.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this answer"
            )
        
        update_data = answer_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(answer, field, value)
        
        answer.updated_at = datetime.utcnow()
        await answer.save()
        
        logger.info(f"Answer updated: {answer.id}")
        return answer
    
    @staticmethod
    async def delete_answer(answer_id: str, user_id: str) -> bool:
        """Delete an answer"""
        answer = await Answer.get(answer_id)
        if not answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found"
            )
        
        if answer.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this answer"
            )
        
        # Delete associated votes
        await Vote.find(Vote.answer_id == answer_id).delete()
        
        # Delete the answer
        await answer.delete()
        
        logger.info(f"Answer deleted: {answer_id}")
        return True
    
    @staticmethod
    async def accept_answer(answer_id: str, user_id: str) -> Answer:
        """Accept an answer (only question owner can do this)"""
        answer = await Answer.get(answer_id)
        if not answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found"
            )
        
        # Check if user owns the question
        question = await Question.get(answer.question_id)
        if not question or question.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only question owner can accept answers"
            )
        
        # Unaccept any previously accepted answer for this question
        await Answer.find({
            "question_id": answer.question_id,
            "is_accepted": True
        }).update({"$set": {"is_accepted": False}})
        
        # Accept this answer
        answer.is_accepted = True
        await answer.save()
        
        logger.info(f"Answer accepted: {answer_id}")
        return answer
    
    @staticmethod
    async def get_answer_with_user_info(answer_id: str) -> Optional[dict]:
        """Get answer with user information and vote score"""
        answer = await Answer.get(answer_id)
        if not answer:
            return None
        
        user = await User.get(answer.user_id)
        if not user:
            return None
        
        # Calculate vote score
        votes = await Vote.find(Vote.answer_id == answer_id).to_list()
        vote_score = sum(vote.value for vote in votes)
        
        return {
            **answer.dict(),
            "username": user.username,
            "user_email": user.email,
            "vote_score": vote_score
        }

