from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from app.models.tag import Tag
from app.models.question import Question
from app.schemas.tag import TagCreate
from app.utils.logger import get_logger

logger = get_logger(__name__)

class TagService:
    
    @staticmethod
    async def create_tag(tag_data: TagCreate) -> Tag:
        """Create a new tag"""
        # Check if tag already exists
        existing_tag = await Tag.find_one(Tag.name == tag_data.name.lower())
        if existing_tag:
            return existing_tag
        
        tag = Tag(name=tag_data.name.lower())
        await tag.insert()
        logger.info(f"Tag created: {tag.name}")
        return tag
    
    @staticmethod
    async def get_tag_by_name(name: str) -> Optional[Tag]:
        """Get tag by name"""
        return await Tag.find_one(Tag.name == name.lower())
    
    @staticmethod
    async def get_tag_by_id(tag_id: str) -> Optional[Tag]:
        """Get tag by ID"""
        return await Tag.get(tag_id)
    
    @staticmethod
    async def get_all_tags(skip: int = 0, limit: int = 100) -> List[Tag]:
        """Get all tags"""
        tags = await Tag.find_all().skip(skip).limit(limit).to_list()
        return tags
    
    @staticmethod
    async def get_popular_tags(limit: int = 20) -> List[dict]:
        """Get popular tags with question counts"""
        tags = await Tag.find_all().to_list()
        tag_stats = []
        
        for tag in tags:
            # Count questions with this tag
            question_count = await Question.find(Question.tags.in_([tag.name])).count()
            
            # Count recent questions (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_count = await Question.find({
                "tags": {"$in": [tag.name]},
                "created_at": {"$gte": thirty_days_ago}
            }).count()
            
            tag_stats.append({
                "name": tag.name,
                "question_count": question_count,
                "recent_questions": recent_count
            })
        
        # Sort by question count
        tag_stats.sort(key=lambda x: x["question_count"], reverse=True)
        return tag_stats[:limit]
    
    @staticmethod
    async def search_tags(query: str, limit: int = 10) -> List[Tag]:
        """Search tags by name"""
        tags = await Tag.find({
            "name": {"$regex": query.lower(), "$options": "i"}
        }).limit(limit).to_list()
        return tags
    
    @staticmethod
    async def get_or_create_tags(tag_names: List[str]) -> List[Tag]:
        """Get existing tags or create new ones"""
        tags = []
        for name in tag_names:
            tag = await TagService.get_tag_by_name(name)
            if not tag:
                tag = await TagService.create_tag(TagCreate(name=name))
            tags.append(tag)
        return tags
    
    @staticmethod
    async def get_tag_stats(tag_name: str) -> dict:
        """Get detailed statistics for a tag"""
        tag = await TagService.get_tag_by_name(tag_name)
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        
        # Count total questions
        total_questions = await Question.find(Question.tags.in_([tag.name])).count()
        
        # Count recent questions (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_questions = await Question.find({
            "tags": {"$in": [tag.name]},
            "created_at": {"$gte": thirty_days_ago}
        }).count()
        
        # Get latest questions
        latest_questions = await Question.find(Question.tags.in_([tag.name]))\
            .sort(-Question.created_at)\
            .limit(5)\
            .to_list()
        
        return {
            "tag": tag,
            "total_questions": total_questions,
            "recent_questions": recent_questions,
            "latest_questions": latest_questions
        }

