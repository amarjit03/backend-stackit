from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from app.schemas.answer import AnswerCreate, AnswerUpdate, AnswerResponse, AnswerWithUser, AcceptAnswerRequest
from app.services.answer_service import AnswerService
from app.core.auth import get_current_active_user
from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/answers", tags=["Answers"])

@router.post("/", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED)
async def create_answer(
    answer_data: AnswerCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new answer"""
    try:
        answer = await AnswerService.create_answer(answer_data, current_user.id)
        return answer
    except Exception as e:
        logger.error(f"Answer creation error: {e}")
        raise

@router.get("/question/{question_id}", response_model=List[AnswerWithUser])
async def get_answers_by_question(
    question_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """Get answers for a specific question"""
    try:
        answers = await AnswerService.get_answers_by_question(
            question_id, skip=skip, limit=limit
        )
        
        # Get user info and vote scores for each answer
        answers_with_info = []
        for answer in answers:
            answer_info = await AnswerService.get_answer_with_user_info(answer.id)
            if answer_info:
                answers_with_info.append(answer_info)
        
        return answers_with_info
    except Exception as e:
        logger.error(f"Get answers error: {e}")
        raise

@router.get("/{answer_id}", response_model=AnswerWithUser)
async def get_answer(answer_id: str):
    """Get a specific answer with user info"""
    answer_data = await AnswerService.get_answer_with_user_info(answer_id)
    if not answer_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Answer not found"
        )
    return answer_data

@router.put("/{answer_id}", response_model=AnswerResponse)
async def update_answer(
    answer_id: str,
    answer_data: AnswerUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update an answer"""
    try:
        answer = await AnswerService.update_answer(
            answer_id, answer_data, current_user.id
        )
        return answer
    except Exception as e:
        logger.error(f"Answer update error: {e}")
        raise

@router.delete("/{answer_id}")
async def delete_answer(
    answer_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete an answer"""
    try:
        await AnswerService.delete_answer(answer_id, current_user.id)
        return {"message": "Answer deleted successfully"}
    except Exception as e:
        logger.error(f"Answer deletion error: {e}")
        raise

@router.post("/accept", response_model=AnswerResponse)
async def accept_answer(
    request: AcceptAnswerRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Accept an answer (only question owner can do this)"""
    try:
        answer = await AnswerService.accept_answer(request.answer_id, current_user.id)
        return answer
    except Exception as e:
        logger.error(f"Accept answer error: {e}")
        raise

@router.get("/user/{user_id}", response_model=List[AnswerResponse])
async def get_answers_by_user(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """Get answers by a specific user"""
    try:
        answers = await AnswerService.get_answers_by_user(
            user_id, skip=skip, limit=limit
        )
        return answers
    except Exception as e:
        logger.error(f"Get user answers error: {e}")
        raise

