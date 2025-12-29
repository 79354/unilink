from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, _schema_generator):
        return {"type": "string"}

class UserBase(BaseModel):
    email: EmailStr
    firstName: str = Field(min_length=2, max_length=50)
    lastName: str = Field(min_length=2, max_length=50)
    location: Optional[str] = ""
    Year: Optional[str] = ""
    picturePath: Optional[str] = ""
    twitterUrl: Optional[str] = ""
    linkedInUrl: Optional[str] = ""

class UserCreate(UserBase):
    password: str = Field(min_length=5)

class UserInDB(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    password: str
    friends: List[str] = []
    viewedProfile: int = 0
    impressions: int = 0
    provider: str = "local"
    discordId: Optional[str] = None
    discordUsername: Optional[str] = ""
    discordDiscriminator: Optional[str] = ""
    discordAvatar: Optional[str] = ""
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserResponse(UserBase):
    id: str = Field(alias="_id")
    friends: List[str] = []
    viewedProfile: int = 0
    impressions: int = 0
    discordUsername: Optional[str] = ""

    class Config:
        populate_by_name = True
