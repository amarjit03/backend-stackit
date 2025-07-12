from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse, CommentWithUser, CommentThread
from app.services.comment_service import CommentService
from app.core.auth import get_current_active_user
from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/comments", tags=["Comments"])

@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new comment on an answer"""
    try:
        comment = await CommentService.create_comment(comment_data, current_user.id)
        return comment
    except Exception as e:
        logger.error(f"Comment creation error: {e}")
        raise

@router.get("/answer/{answer_id}", response_model=List[CommentWithUser])
async def get_comments_by_answer(answer_id: str):
    """Get all comments for an answer (flat list)"""
    try:
        comments = await CommentService.get_comments_by_answer(answer_id)
        return comments
    except Exception as e:
        logger.error(f"Get comments error: {e}")
        raise

@router.get("/answer/{answer_id}/threads", response_model=List[CommentThread])
async def get_comment_threads(answer_id: str):
    """Get comments organized in threads (nested structure)"""
    try:
        threads = await CommentService.get_comment_threads(answer_id)
        return threads
    except Exception as e:
        logger.error(f"Get comment threads error: {e}")
        raise

@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: str):
    """Get a specific comment"""
    comment = await CommentService.get_comment_by_id(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    return comment

@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: str,
    comment_data: CommentUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update a comment"""
    try:
        comment = await CommentService.update_comment(
            comment_id, comment_data, current_user.id
        )
        return comment
    except Exception as e:
        logger.error(f"Comment update error: {e}")
        raise

@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a comment and all its replies"""
    try:
        await CommentService.delete_comment(comment_id, current_user.id)
        return {"message": "Comment deleted successfully"}
    except Exception as e:
        logger.error(f"Comment deletion error: {e}")
        raise

@router.get("/user/{user_id}", response_model=List[CommentWithUser])
async def get_comments_by_user(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """Get comments by a specific user"""
    try:
        comments = await CommentService.get_user_comments(
            user_id, skip=skip, limit=limit
        )
        return comments
    except Exception as e:
        logger.error(f"Get user comments error: {e}")
        raise

@router.get("/answer/{answer_id}/count")
async def get_comment_count(answer_id: str):
    """Get total comment count for an answer"""
    try:
        count = await CommentService.get_comment_count_by_answer(answer_id)
        return {"answer_id": answer_id, "comment_count": count}
    except Exception as e:
        logger.error(f"Get comment count error: {e}")
        raise

@router.get("/search/", response_model=List[CommentWithUser])
async def search_comments(
    q: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """Search comments by text content"""
    try:
        comments = await CommentService.search_comments(q, skip=skip, limit=limit)
        return comments
    except Exception as e:
        logger.error(f"Search comments error: {e}")
        raise

@router.post("/{comment_id}/reply", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def reply_to_comment(
    comment_id: str,
    reply_text: str = Query(..., min_length=1, max_length=1000),
    current_user: User = Depends(get_current_active_user)
):
    """Reply to a specific comment (convenience endpoint)"""
    try:
        # Get the parent comment to find the answer_id
        parent_comment = await CommentService.get_comment_by_id(comment_id)
        if not parent_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent comment not found"
            )
        
        comment_data = CommentCreate(
            answer_id=parent_comment.answer_id,
            parent_id=comment_id,
            text=reply_text
        )
        
        comment = await CommentService.create_comment(comment_data, current_user.id)
        return comment
    except Exception as e:
        logger.error(f"Reply to comment error: {e}")
        raise

