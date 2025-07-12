from typing import List, Optional
from fastapi import HTTPException, status
from datetime import datetime
from app.models.question import Question
from app.models.answer import Answer
from app.models.user import User
from app.schemas.question import QuestionCreate, QuestionUpdate
from app.utils.logger import get_logger

logger = get_logger(__name__)

class QuestionService:
    
    @staticmethod
    async def create_question(question_data: QuestionCreate, user_id: str) -> Question:
        """Create a new question"""
        question = Question(
            user_id=user_id,
            title=question_data.title,
            description=question_data.description,
            tags=question_data.tags
        )
        
        await question.insert()
        logger.info(f"Question created: {question.id} by user {user_id}")
        return question
    
    @staticmethod
    async def get_question_by_id(question_id: str) -> Optional[Question]:
        """Get question by ID"""
        return await Question.get(question_id)
    
    @staticmethod
    async def get_questions(
        skip: int = 0,
        limit: int = 20,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None
    ) -> List[Question]:
        """Get questions with optional filtering"""
        query = Question.find_all()
        
        if tags:
            query = query.find(Question.tags.in_(tags))
        
        if search:
            # Simple text search in title and description
            query = query.find({
                "$or": [
                    {"title": {"$regex": search, "$options": "i"}},
                    {"description": {"$regex": search, "$options": "i"}}
                ]
            })
        
        questions = await query.sort(-Question.created_at).skip(skip).limit(limit).to_list()
        return questions
    
    @staticmethod
    async def get_questions_by_user(user_id: str, skip: int = 0, limit: int = 20) -> List[Question]:
        """Get questions by user"""
        questions = await Question.find(Question.user_id == user_id)\
            .sort(-Question.created_at)\
            .skip(skip)\
            .limit(limit)\
            .to_list()
        return questions
    
    @staticmethod
    async def update_question(question_id: str, question_data: QuestionUpdate, user_id: str) -> Question:
        """Update a question"""
        question = await Question.get(question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        if question.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this question"
            )
        
        update_data = question_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(question, field, value)
        
        question.updated_at = datetime.utcnow()
        await question.save()
        
        logger.info(f"Question updated: {question.id}")
        return question
    
    @staticmethod
    async def delete_question(question_id: str, user_id: str) -> bool:
        """Delete a question"""
        question = await Question.get(question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        if question.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this question"
            )
        
        # Delete associated answers
        await Answer.find(Answer.question_id == question_id).delete()
        
        # Delete the question
        await question.delete()
        
        logger.info(f"Question deleted: {question_id}")
        return True
    
    @staticmethod
    async def get_question_with_user_info(question_id: str) -> Optional[dict]:
        """Get question with user information"""
        question = await Question.get(question_id)
        if not question:
            return None
        
        user = await User.get(question.user_id)
        if not user:
            return None
        
        # Count answers
        answer_count = await Answer.find(Answer.question_id == question_id).count()
        
        # Check for accepted answer
        accepted_answer = await Answer.find_one({
            "question_id": question_id,
            "is_accepted": True
        })
        
        return {
            **question.dict(),
            "username": user.username,
            "user_email": user.email,
            "answer_count": answer_count,
            "accepted_answer_id": accepted_answer.id if accepted_answer else None
        }

