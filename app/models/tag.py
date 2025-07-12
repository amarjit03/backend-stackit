from beanie import Document
from pydantic import Field
import uuid

class Tag(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    name: str = Field(..., unique=True, index=True)
    
    class Settings:
        name = "tags"
        indexes = [
            "name",
        ]
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"

