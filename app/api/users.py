from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.core.database import get_database
from app.core.security import verify_token
from app.models.user import UserResponse
from app.core.redis_client import publish_notification_event, NotificationChannels
from pydantic import BaseModel
from bson import ObjectId

router = APIRouter()

class SocialUrlsUpdate(BaseModel):
    twitterUrl: str = ""
    linkedInUrl: str = ""

class SearchRequest(BaseModel):
    query: str

@router.get("/{id}", response_model=UserResponse)
async def get_user(id: str, current_user: dict = Depends(verify_token)):
    db = get_database()
    users_collection = db.users
    
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    user = await users_collection.find_one({"_id": ObjectId(id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Track profile view
    viewer_id = current_user.get("id")
    if viewer_id and viewer_id != id:
        viewer = await users_collection.find_one({"_id": ObjectId(viewer_id)})
        if viewer:
            await publish_notification_event(
                NotificationChannels.PROFILE_VIEW,
                {
                    "userId": id,
                    "actorId": viewer_id,
                    "actorName": f"{viewer['firstName']} {viewer['lastName']}",
                    "actorPicture": viewer.get("picturePath", "")
                }
            )
    
    user["_id"] = str(user["_id"])
    return user

@router.get("/{id}/friends", response_model=List[UserResponse])
async def get_user_friends(id: str, current_user: dict = Depends(verify_token)):
    db = get_database()
    users_collection = db.users
    
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    user = await users_collection.find_one({"_id": ObjectId(id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get friend details
    friends = []
    for friend_id in user.get("friends", []):
        if ObjectId.is_valid(friend_id):
            friend = await users_collection.find_one({"_id": ObjectId(friend_id)})
            if friend:
                friend["_id"] = str(friend["_id"])
                friends.append(friend)
    
    return friends

@router.patch("/{id}/{friendId}", response_model=List[UserResponse])
async def add_remove_friend(
    id: str, 
    friendId: str, 
    current_user: dict = Depends(verify_token)
):
    db = get_database()
    users_collection = db.users
    
    if not ObjectId.is_valid(id) or not ObjectId.is_valid(friendId):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    user = await users_collection.find_one({"_id": ObjectId(id)})
    friend = await users_collection.find_one({"_id": ObjectId(friendId)})
    
    if not user or not friend:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_friends = user.get("friends", [])
    friend_friends = friend.get("friends", [])
    
    if friendId in user_friends:
        # Remove friend
        user_friends.remove(friendId)
        if id in friend_friends:
            friend_friends.remove(id)
    else:
        # Add friend
        user_friends.append(friendId)
        friend_friends.append(id)
        
        # Send notification
        await publish_notification_event(
            NotificationChannels.FRIEND_REQUEST,
            {
                "userId": friendId,
                "actorId": id,
                "actorName": f"{user['firstName']} {user['lastName']}",
                "actorPicture": user.get("picturePath", "")
            }
        )
    
    # Update both users
    await users_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"friends": user_friends}}
    )
    await users_collection.update_one(
        {"_id": ObjectId(friendId)},
        {"$set": {"friends": friend_friends}}
    )
    
    # Return updated friends list
    friends = []
    for friend_id in user_friends:
        if ObjectId.is_valid(friend_id):
            f = await users_collection.find_one({"_id": ObjectId(friend_id)})
            if f:
                f["_id"] = str(f["_id"])
                friends.append(f)
    
    return friends

@router.patch("/{id}/social", response_model=UserResponse)
async def update_social_urls(
    id: str,
    urls: SocialUrlsUpdate,
    current_user: dict = Depends(verify_token)
):
    db = get_database()
    users_collection = db.users
    
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    result = await users_collection.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": {
            "twitterUrl": urls.twitterUrl,
            "linkedInUrl": urls.linkedInUrl
        }},
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    
    result["_id"] = str(result["_id"])
    return result

@router.post("/search", response_model=List[UserResponse])
async def search_users(search: SearchRequest):
    db = get_database()
    users_collection = db.users
    
    if not search.query or not search.query.strip():
        raise HTTPException(status_code=400, detail="Invalid or missing search query")
    
    # Case-insensitive regex search
    users = await users_collection.find({
        "$or": [
            {"firstName": {"$regex": search.query, "$options": "i"}},
            {"lastName": {"$regex": search.query, "$options": "i"}}
        ]
    }).to_list(length=100)
    
    for user in users:
        user["_id"] = str(user["_id"])
    
    return users