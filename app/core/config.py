from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Application
    app_name: str = "StackIt"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Database
    mongodb_url: str = "mongodb+srv://amarjit3587:HiGSA1XNRikmAzXU@cluster0.vjdpwro.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    database_name: str = "stackit_db"
    
    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080", "*"]
    
    # File Upload
    max_file_size: int = 5242880  # 5MB
    upload_dir: str = "uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

