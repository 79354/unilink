from datetime import datetime
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field
from models.user import PyObjectId

class MessageModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    conversationId: PyObjectId
    sender: PyObjectId
    content: str
    read: bool = False
    readAt: Optional[datetime] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "conversationId": "507f1f77bcf86cd799439011",
                "sender": "507f1f77bcf86cd799439012",
                "content": "Hello, how are you?",
                "read": False
            }
        }