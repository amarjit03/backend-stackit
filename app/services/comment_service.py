from typing import List, Optional, Dict
from fastapi import HTTPException, status
from datetime import datetime
from app.models.comment import Comment
from app.models.answer import Answer
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate
from app.services.notification_service import NotificationService
from app.utils.logger import get_logger

logger = get_logger(__name__)

class CommentService:
    
    @staticmethod
    async def create_comment(comment_data: CommentCreate, user_id: str) -> Comment:
        """Create a new comment"""
        # Verify answer exists
        answer = await Answer.get(comment_data.answer_id)
        if not answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found"
            )
        
        # If parent_id is provided, verify parent comment exists
        if comment_data.parent_id:
            parent_comment = await Comment.get(comment_data.parent_id)
            if not parent_comment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent comment not found"
                )
            
            # Ensure parent comment belongs to the same answer
            if parent_comment.answer_id != comment_data.answer_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent comment must belong to the same answer"
                )
        
        comment = Comment(
            user_id=user_id,
            answer_id=comment_data.answer_id,
            parent_id=comment_data.parent_id,
            text=comment_data.text
        )
        
        await comment.insert()
        
        # Send notification to answer owner
        if answer.user_id != user_id:
            user = await User.get(user_id)
            if user:
                await NotificationService.notify_comment_posted(
                    comment_data.answer_id, user.username, answer.user_id
                )
        
        logger.info(f"Comment created: {comment.id} on answer {comment_data.answer_id}")
        return comment
    
    @staticmethod
    async def get_comment_by_id(comment_id: str) -> Optional[Comment]:
        """Get comment by ID"""
        return await Comment.get(comment_id)
    
    @staticmethod
    async def get_comments_by_answer(answer_id: str) -> List[Dict]:
        """Get all comments for an answer with user info"""
        comments = await Comment.find(Comment.answer_id == answer_id)\
            .sort(Comment.created_at)\
            .to_list()
        
        # Get user info for each comment
        comments_with_users = []
        for comment in comments:
            user = await User.get(comment.user_id)
            if user:
                comment_dict = {
                    **comment.dict(),
                    "username": user.username,
                    "user_email": user.email
                }
                comments_with_users.append(comment_dict)
        
        return comments_with_users
    
    @staticmethod
    async def get_comment_threads(answer_id: str) -> List[Dict]:
        """Get comments organized in threads (nested structure)"""
        comments = await CommentService.get_comments_by_answer(answer_id)
        
        # Separate root comments and replies
        root_comments = []
        replies_map = {}
        
        for comment in comments:
            if comment["parent_id"] is None:
                comment["replies"] = []
                comment["reply_count"] = 0
                root_comments.append(comment)
            else:
                parent_id = comment["parent_id"]
                if parent_id not in replies_map:
                    replies_map[parent_id] = []
                replies_map[parent_id].append(comment)
        
        # Build nested structure
        def build_thread(comment_dict):
            comment_id = comment_dict["id"]
            if comment_id in replies_map:
                replies = replies_map[comment_id]
                comment_dict["replies"] = [build_thread(reply) for reply in replies]
                comment_dict["reply_count"] = len(replies)
            return comment_dict
        
        # Build threads for root comments
        threads = [build_thread(comment) for comment in root_comments]
        
        return threads
    
    @staticmethod
    async def update_comment(comment_id: str, comment_data: CommentUpdate, user_id: str) -> Comment:
        """Update a comment"""
        comment = await Comment.get(comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        if comment.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this comment"
            )
        
        update_data = comment_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(comment, field, value)
        
        await comment.save()
        
        logger.info(f"Comment updated: {comment.id}")
        return comment
    
    @staticmethod
    async def delete_comment(comment_id: str, user_id: str) -> bool:
        """Delete a comment and all its replies"""
        comment = await Comment.get(comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        if comment.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this comment"
            )
        
        # Delete all replies to this comment recursively
        await CommentService._delete_comment_and_replies(comment_id)
        
        logger.info(f"Comment deleted: {comment_id}")
        return True
    
    @staticmethod
    async def _delete_comment_and_replies(comment_id: str):
        """Recursively delete a comment and all its replies"""
        # Find all replies to this comment
        replies = await Comment.find(Comment.parent_id == comment_id).to_list()
        
        # Recursively delete replies
        for reply in replies:
            await CommentService._delete_comment_and_replies(reply.id)
        
        # Delete the comment itself
        comment = await Comment.get(comment_id)
        if comment:
            await comment.delete()
    
    @staticmethod
    async def get_user_comments(user_id: str, skip: int = 0, limit: int = 20) -> List[Dict]:
        """Get comments by a user"""
        comments = await Comment.find(Comment.user_id == user_id)\
            .sort(-Comment.created_at)\
            .skip(skip)\
            .limit(limit)\
            .to_list()
        
        # Get user info and answer info for each comment
        comments_with_info = []
        for comment in comments:
            user = await User.get(comment.user_id)
            answer = await Answer.get(comment.answer_id)
            
            if user and answer:
                comment_dict = {
                    **comment.dict(),
                    "username": user.username,
                    "user_email": user.email,
                    "answer_description": answer.description[:100] + "..." if len(answer.description) > 100 else answer.description
                }
                comments_with_info.append(comment_dict)
        
        return comments_with_info
    
    @staticmethod
    async def get_comment_count_by_answer(answer_id: str) -> int:
        """Get total comment count for an answer"""
        return await Comment.find(Comment.answer_id == answer_id).count()
    
    @staticmethod
    async def search_comments(query: str, skip: int = 0, limit: int = 20) -> List[Dict]:
        """Search comments by text content"""
        comments = await Comment.find({
            "text": {"$regex": query, "$options": "i"}
        }).sort(-Comment.created_at).skip(skip).limit(limit).to_list()
        
        # Get user info for each comment
        comments_with_users = []
        for comment in comments:
            user = await User.get(comment.user_id)
            if user:
                comment_dict = {
                    **comment.dict(),
                    "username": user.username,
                    "user_email": user.email
                }
                comments_with_users.append(comment_dict)
        
        return comments_with_users

