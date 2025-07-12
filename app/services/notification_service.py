from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.models.question import Question
from app.schemas.notification import NotificationCreate
from app.utils.logger import get_logger

logger = get_logger(__name__)

class NotificationService:
    
    @staticmethod
    async def create_notification(notification_data: NotificationCreate) -> Notification:
        """Create a new notification"""
        notification = Notification(
            user_id=notification_data.user_id,
            type=notification_data.type,
            content=notification_data.content,
            question_id=notification_data.question_id
        )
        
        await notification.insert()
        logger.info(f"Notification created: {notification.id} for user {notification_data.user_id}")
        return notification
    
    @staticmethod
    async def get_user_notifications(
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        unread_only: bool = False
    ) -> List[Notification]:
        """Get notifications for a user"""
        query = {"user_id": user_id}
        if unread_only:
            query["is_read"] = False
        
        notifications = await Notification.find(query)\
            .sort(-Notification.created_at)\
            .skip(skip)\
            .limit(limit)\
            .to_list()
        
        return notifications
    
    @staticmethod
    async def mark_notification_as_read(notification_id: str, user_id: str) -> Notification:
        """Mark a notification as read"""
        notification = await Notification.get(notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        if notification.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this notification"
            )
        
        notification.is_read = True
        await notification.save()
        
        logger.info(f"Notification marked as read: {notification_id}")
        return notification
    
    @staticmethod
    async def mark_all_as_read(user_id: str) -> int:
        """Mark all notifications as read for a user"""
        result = await Notification.find({
            "user_id": user_id,
            "is_read": False
        }).update({"$set": {"is_read": True}})
        
        logger.info(f"All notifications marked as read for user: {user_id}")
        return result.modified_count
    
    @staticmethod
    async def get_notification_stats(user_id: str) -> dict:
        """Get notification statistics for a user"""
        total_count = await Notification.find({"user_id": user_id}).count()
        unread_count = await Notification.find({
            "user_id": user_id,
            "is_read": False
        }).count()
        
        # Recent notifications (last 24 hours)
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        recent_count = await Notification.find({
            "user_id": user_id,
            "created_at": {"$gte": twenty_four_hours_ago}
        }).count()
        
        return {
            "total_count": total_count,
            "unread_count": unread_count,
            "recent_count": recent_count
        }
    
    @staticmethod
    async def delete_notification(notification_id: str, user_id: str) -> bool:
        """Delete a notification"""
        notification = await Notification.get(notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        if notification.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this notification"
            )
        
        await notification.delete()
        logger.info(f"Notification deleted: {notification_id}")
        return True
    
    # Helper methods for creating specific types of notifications
    
    @staticmethod
    async def notify_answer_posted(question_id: str, answerer_username: str):
        """Notify question owner when someone answers their question"""
        question = await Question.get(question_id)
        if not question:
            return
        
        content = f"{answerer_username} answered your question: {question.title}"
        
        await NotificationService.create_notification(NotificationCreate(
            user_id=question.user_id,
            type=NotificationType.ANSWER,
            content=content,
            question_id=question_id
        ))
    
    @staticmethod
    async def notify_comment_posted(answer_id: str, commenter_username: str, answer_owner_id: str):
        """Notify answer owner when someone comments on their answer"""
        content = f"{commenter_username} commented on your answer"
        
        await NotificationService.create_notification(NotificationCreate(
            user_id=answer_owner_id,
            type=NotificationType.COMMENT,
            content=content
        ))
    
    @staticmethod
    async def notify_mention(mentioned_user_id: str, mentioner_username: str, context: str):
        """Notify user when they are mentioned"""
        content = f"{mentioner_username} mentioned you in {context}"
        
        await NotificationService.create_notification(NotificationCreate(
            user_id=mentioned_user_id,
            type=NotificationType.MENTION,
            content=content
        ))
    
    @staticmethod
    async def notify_vote_received(answer_owner_id: str, voter_username: str, vote_type: str):
        """Notify answer owner when their answer receives a vote"""
        content = f"{voter_username} {vote_type}d your answer"
        
        await NotificationService.create_notification(NotificationCreate(
            user_id=answer_owner_id,
            type=NotificationType.VOTE,
            content=content
        ))

