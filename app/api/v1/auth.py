from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.services.user_service import UserService
from app.core.auth import get_current_active_user
from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        user = await UserService.create_user(user_data)
        return user
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """Login user and return access token"""
    try:
        result = await UserService.login_user(user_data.username, user_data.password)
        return {
            "access_token": result["access_token"],
            "token_type": result["token_type"]
        }
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 compatible token endpoint"""
    try:
        result = await UserService.login_user(form_data.username, form_data.password)
        return {
            "access_token": result["access_token"],
            "token_type": result["token_type"]
        }
    except Exception as e:
        logger.error(f"Token login error: {e}")
        raise

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@router.get("/verify-token")
async def verify_token(current_user: User = Depends(get_current_active_user)):
    """Verify if token is valid"""
    return {"valid": True, "user_id": current_user.id}

