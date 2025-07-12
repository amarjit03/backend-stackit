from beanie import Document
from pydantic import Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid

class UserRole(str, Enum):
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"

class User(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    username: str = Field(..., unique=True, index=True)
    email: EmailStr = Field(..., unique=True, index=True)
    password_hash: str = Field(...)
    role: UserRole = Field(default=UserRole.USER)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "users"
        indexes = [
            "username",
            "email",
        ]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

