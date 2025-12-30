from pydantic import BaseModel
from typing import Optional

class UserSearchResponse(BaseModel):
    id: str = None
    firstName: str
    lastName: str
    picturePath: str
    isOnline: bool = False

    class Config:
        from_attributes = True

class OnlineStatusRequest(BaseModel):
    userIds: list[str]

class OnlineStatusResponse(BaseModel):
    onlineUsers: list[str]