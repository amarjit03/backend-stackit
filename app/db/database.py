from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def connect_to_mongo():
    """Create database connection"""
    try:
        db.client = AsyncIOMotorClient(settings.mongodb_url)
        db.database = db.client[settings.database_name]
        
        # Import all models here
        from app.models.user import User
        from app.models.question import Question
        from app.models.answer import Answer
        from app.models.tag import Tag
        from app.models.vote import Vote
        from app.models.notification import Notification
        from app.models.mcq import MCQQuiz, MCQQuestion
        from app.models.comment import Comment
        from app.models.question_tag import QuestionTag
        
        # Initialize beanie with the models
        await init_beanie(
            database=db.database,
            document_models=[
                User, Question, Answer, Tag, Vote, 
                Notification, MCQQuiz, MCQQuestion, 
                Comment, QuestionTag
            ]
        )
        
        logger.info("Connected to MongoDB successfully")
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    try:
        if db.client:
            db.client.close()
            logger.info("Disconnected from MongoDB")
    except Exception as e:
        logger.error(f"Error disconnecting from MongoDB: {e}")

def get_database():
    """Get database instance"""
    return db.database

