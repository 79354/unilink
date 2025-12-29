from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from bson import ObjectId
from app.models.user import PyObjectId

class PostCreate(BaseModel):
    userId: str
    description: Optional[str] = ""
    picturePath: Optional[str] = ""

class PostInDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    userId: str
    firstName: str
    lastName: str
    location: Optional[str] = ""
    description: Optional[str] = ""
    picturePath: Optional[str] = ""
    userPicturePath: Optional[str] = ""
    likes: Dict[str, bool] = {}
    comments: List[str] = []
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class PostResponse(BaseModel):
    id: str = Field(alias="_id")
    userId: str
    firstName: str
    lastName: str
    location: Optional[str] = ""
    description: Optional[str] = ""
    picturePath: Optional[str] = ""
    userPicturePath: Optional[str] = ""
    likes: Dict[str, bool] = {}
    comments: List[str] = []
    createdAt: datetime
    updatedAt: datetime

    class Config:
        populate_by_name = True