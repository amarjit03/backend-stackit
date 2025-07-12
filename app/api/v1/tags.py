from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from app.schemas.tag import TagCreate, TagResponse, TagStats
from app.services.tag_service import TagService
from app.core.auth import get_current_active_user
from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/tags", tags=["Tags"])

@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new tag"""
    try:
        tag = await TagService.create_tag(tag_data)
        return tag
    except Exception as e:
        logger.error(f"Tag creation error: {e}")
        raise

@router.get("/", response_model=List[TagResponse])
async def get_all_tags(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500)
):
    """Get all tags"""
    try:
        tags = await TagService.get_all_tags(skip=skip, limit=limit)
        return tags
    except Exception as e:
        logger.error(f"Get tags error: {e}")
        raise

@router.get("/popular", response_model=List[TagStats])
async def get_popular_tags(
    limit: int = Query(20, ge=1, le=100)
):
    """Get popular tags with statistics"""
    try:
        tag_stats = await TagService.get_popular_tags(limit=limit)
        return tag_stats
    except Exception as e:
        logger.error(f"Get popular tags error: {e}")
        raise

@router.get("/search", response_model=List[TagResponse])
async def search_tags(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50)
):
    """Search tags by name"""
    try:
        tags = await TagService.search_tags(q, limit=limit)
        return tags
    except Exception as e:
        logger.error(f"Search tags error: {e}")
        raise

@router.get("/{tag_name}")
async def get_tag_details(tag_name: str):
    """Get detailed information about a tag"""
    try:
        tag_info = await TagService.get_tag_stats(tag_name)
        return tag_info
    except Exception as e:
        logger.error(f"Get tag details error: {e}")
        raise

@router.get("/{tag_name}/questions")
async def get_questions_by_tag(
    tag_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """Get questions for a specific tag"""
    try:
        from app.services.question_service import QuestionService
        questions = await QuestionService.get_questions(
            skip=skip,
            limit=limit,
            tags=[tag_name]
        )
        return questions
    except Exception as e:
        logger.error(f"Get questions by tag error: {e}")
        raise

