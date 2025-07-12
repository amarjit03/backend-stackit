from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.schemas.question import QuestionCreate, QuestionUpdate, QuestionResponse, QuestionWithUser
from app.services.question_service import QuestionService
from app.core.auth import get_current_active_user
from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/questions", tags=["Questions"])

@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    question_data: QuestionCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new question"""
    try:
        question = await QuestionService.create_question(question_data, current_user.id)
        return question
    except Exception as e:
        logger.error(f"Question creation error: {e}")
        raise

@router.get("/", response_model=List[QuestionResponse])
async def get_questions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    tags: Optional[List[str]] = Query(None),
    search: Optional[str] = Query(None)
):
    """Get questions with optional filtering"""
    try:
        questions = await QuestionService.get_questions(
            skip=skip,
            limit=limit,
            tags=tags,
            search=search
        )
        return questions
    except Exception as e:
        logger.error(f"Get questions error: {e}")
        raise

@router.get("/{question_id}", response_model=QuestionWithUser)
async def get_question(question_id: str):
    """Get a specific question with user info"""
    question_data = await QuestionService.get_question_with_user_info(question_id)
    if not question_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    return question_data

@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: str,
    question_data: QuestionUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update a question"""
    try:
        question = await QuestionService.update_question(
            question_id, question_data, current_user.id
        )
        return question
    except Exception as e:
        logger.error(f"Question update error: {e}")
        raise

@router.delete("/{question_id}")
async def delete_question(
    question_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a question"""
    try:
        await QuestionService.delete_question(question_id, current_user.id)
        return {"message": "Question deleted successfully"}
    except Exception as e:
        logger.error(f"Question deletion error: {e}")
        raise

@router.get("/user/{user_id}", response_model=List[QuestionResponse])
async def get_questions_by_user(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """Get questions by a specific user"""
    try:
        questions = await QuestionService.get_questions_by_user(
            user_id, skip=skip, limit=limit
        )
        return questions
    except Exception as e:
        logger.error(f"Get user questions error: {e}")
        raise

