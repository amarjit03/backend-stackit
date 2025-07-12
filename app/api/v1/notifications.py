from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from app.schemas.notification import NotificationResponse, NotificationUpdate, NotificationStats
from app.services.notification_service import NotificationService
from app.core.auth import get_current_active_user
from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", response_model=List[NotificationResponse])
async def get_my_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's notifications"""
    try:
        notifications = await NotificationService.get_user_notifications(
            current_user.id,
            skip=skip,
            limit=limit,
            unread_only=unread_only
        )
        return notifications
    except Exception as e:
        logger.error(f"Get notifications error: {e}")
        raise

@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    current_user: User = Depends(get_current_active_user)
):
    """Get notification statistics for current user"""
    try:
        stats = await NotificationService.get_notification_stats(current_user.id)
        return stats
    except Exception as e:
        logger.error(f"Get notification stats error: {e}")
        raise

@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Mark a notification as read"""
    try:
        notification = await NotificationService.mark_notification_as_read(
            notification_id, current_user.id
        )
        return notification
    except Exception as e:
        logger.error(f"Mark notification as read error: {e}")
        raise

@router.put("/mark-all-read")
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_active_user)
):
    """Mark all notifications as read"""
    try:
        count = await NotificationService.mark_all_as_read(current_user.id)
        return {"message": f"{count} notifications marked as read"}
    except Exception as e:
        logger.error(f"Mark all notifications as read error: {e}")
        raise

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a notification"""
    try:
        await NotificationService.delete_notification(notification_id, current_user.id)
        return {"message": "Notification deleted successfully"}
    except Exception as e:
        logger.error(f"Delete notification error: {e}")
        raise

@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_active_user)
):
    """Get count of unread notifications"""
    try:
        stats = await NotificationService.get_notification_stats(current_user.id)
        return {"unread_count": stats["unread_count"]}
    except Exception as e:
        logger.error(f"Get unread count error: {e}")
        raise

