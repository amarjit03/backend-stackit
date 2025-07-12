from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService
from app.core.auth import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update current user profile"""
    try:
        updated_user = await UserService.update_user(current_user.id, user_data)
        return updated_user
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: str):
    """Get user by ID (public endpoint)"""
    user = await UserService.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/username/{username}", response_model=UserResponse)
async def get_user_by_username(username: str):
    """Get user by username (public endpoint)"""
    user = await UserService.get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user)
):
    """Get all users (admin only)"""
    users = await User.find_all().skip(skip).limit(limit).to_list()
    return users

