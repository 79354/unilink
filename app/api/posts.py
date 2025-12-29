from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from app.core.database import get_database
from app.core.security import verify_token
from app.models.post import PostCreate, PostResponse
from app.core.redis_client import publish_notification_event, NotificationChannels
from bson import ObjectId
from pydantic import BaseModel

router = APIRouter()

class LikeRequest(BaseModel):
    userId: str

@router.post("", response_model=List[PostResponse], status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    current_user: dict = Depends(verify_token)
):
    db = get_database()
    users_collection = db.users
    posts_collection = db.posts
    
    # Get user info
    if not ObjectId.is_valid(post_data.userId):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    user = await users_collection.find_one({"_id": ObjectId(post_data.userId)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create post
    new_post = {
        "userId": post_data.userId,
        "firstName": user["firstName"],
        "lastName": user["lastName"],
        "location": user.get("location", ""),
        "description": post_data.description or "",
        "userPicturePath": user.get("picturePath", ""),
        "picturePath": post_data.picturePath or "",
        "likes": {},
        "comments": []
    }
    
    result = await posts_collection.insert_one(new_post)
    created_post = await posts_collection.find_one({"_id": result.inserted_id})
    
    # Notify friends
    if user.get("friends"):
        for friend_id in user["friends"]:
            await publish_notification_event(
                NotificationChannels.FRIEND_POST,
                {
                    "userId": friend_id,
                    "actorId": post_data.userId,
                    "actorName": f"{user['firstName']} {user['lastName']}",
                    "actorPicture": user.get("picturePath", ""),
                    "relatedId": str(created_post["_id"]),
                    "metadata": {
                        "postDescription": post_data.description[:100] if post_data.description else ""
                    }
                }
            )
    
    # Return all posts
    posts = await posts_collection.find().to_list(length=1000)
    for post in posts:
        post["_id"] = str(post["_id"])
    
    return posts

@router.get("", response_model=List[PostResponse])
async def get_feed_posts(current_user: dict = Depends(verify_token)):
    db = get_database()
    posts_collection = db.posts
    
    posts = await posts_collection.find().to_list(length=1000)
    for post in posts:
        post["_id"] = str(post["_id"])
    
    return posts

@router.get("/{userId}/posts", response_model=List[PostResponse])
async def get_user_posts(userId: str, current_user: dict = Depends(verify_token)):
    db = get_database()
    posts_collection = db.posts
    
    posts = await posts_collection.find({"userId": userId}).to_list(length=1000)
    for post in posts:
        post["_id"] = str(post["_id"])
    
    return posts

@router.patch("/{id}/like", response_model=PostResponse)
async def like_post(
    id: str,
    like_data: LikeRequest,
    current_user: dict = Depends(verify_token)
):
    db = get_database()
    posts_collection = db.posts
    users_collection = db.users
    
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid post ID")
    
    post = await posts_collection.find_one({"_id": ObjectId(id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    likes = post.get("likes", {})
    user_id = like_data.userId
    
    if user_id in likes:
        # Unlike
        del likes[user_id]
    else:
        # Like
        likes[user_id] = True
        
        # Send notification (if not self-like)
        if post["userId"] != user_id:
            liker = await users_collection.find_one({"_id": ObjectId(user_id)})
            if liker:
                await publish_notification_event(
                    NotificationChannels.LIKE,
                    {
                        "userId": post["userId"],
                        "actorId": user_id,
                        "actorName": f"{liker['firstName']} {liker['lastName']}",
                        "actorPicture": liker.get("picturePath", ""),
                        "relatedId": id
                    }
                )
    
    # Update post
    updated_post = await posts_collection.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": {"likes": likes}},
        return_document=True
    )
    
    updated_post["_id"] = str(updated_post["_id"])
    return updated_post