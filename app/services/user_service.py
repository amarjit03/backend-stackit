from typing import Optional
from fastapi import HTTPException, status
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password, create_access_token
from app.utils.logger import get_logger

logger = get_logger(__name__)

class UserService:
    
    @staticmethod
    async def create_user(user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if username already exists
        existing_user = await User.find_one(User.username == user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        existing_email = await User.find_one(User.email == user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password and create user
        hashed_password = get_password_hash(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            role=UserRole.USER
        )
        
        await user.insert()
        logger.info(f"User created: {user.username}")
        return user
    
    @staticmethod
    async def authenticate_user(username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = await User.find_one(User.username == username)
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    @staticmethod
    async def login_user(username: str, password: str) -> dict:
        """Login user and return access token"""
        user = await UserService.authenticate_user(username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(data={"sub": user.id})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[User]:
        """Get user by ID"""
        return await User.get(user_id)
    
    @staticmethod
    async def get_user_by_username(username: str) -> Optional[User]:
        """Get user by username"""
        return await User.find_one(User.username == username)
    
    @staticmethod
    async def update_user(user_id: str, user_data: UserUpdate) -> User:
        """Update user information"""
        user = await User.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        update_data = user_data.dict(exclude_unset=True)
        
        # Check if new username is already taken
        if "username" in update_data:
            existing_user = await User.find_one(User.username == update_data["username"])
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Check if new email is already taken
        if "email" in update_data:
            existing_email = await User.find_one(User.email == update_data["email"])
            if existing_email and existing_email.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already taken"
                )
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await user.save()
        logger.info(f"User updated: {user.username}")
        return user

