from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Dict, Optional
from bson import ObjectId
from app.models.user import PyObjectId

class OTPCreate(BaseModel):
    email: EmailStr
    firstName: str
    lastName: str
    password: str
    picturePath: Optional[str] = ""
    location: Optional[str] = ""
    Year: Optional[str] = ""

class OTPInDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: str
    otp: str
    userData: Dict
    attempts: int = 0
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}