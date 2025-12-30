from datetime import datetime
from typing import List, Optional, Dict
from bson import ObjectId
from pydantic import BaseModel, Field
from models.user import PyObjectId

class ConversationModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    participants: List[PyObjectId]
    lastMessage: Optional[PyObjectId] = None
    lastMessageAt: datetime = Field(default_factory=datetime.utcnow)
    unreadCount: Dict[str, int] = {}
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "participants": ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012"],
                "lastMessage": "507f1f77bcf86cd799439013",
                "lastMessageAt": "2024-01-01T00:00:00Z",
                "unreadCount": {"507f1f77bcf86cd799439011": 0, "507f1f77bcf86cd799439012": 5}
            }
        }