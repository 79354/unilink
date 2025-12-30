from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SendMessageRequest(BaseModel):
    recipientId: str
    content: str

class UserInfo(BaseModel):
    id: str = None
    firstName: str
    lastName: str
    picturePath: str

class MessageResponse(BaseModel):
    id: str = None
    conversationId: str
    sender: UserInfo
    content: str
    read: bool
    readAt: Optional[datetime] = None
    createdAt: datetime

    class Config:
        from_attributes = True