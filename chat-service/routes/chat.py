from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId
from datetime import datetime
from typing import List

from middleware.auth import verify_token
from core.database import get_database
from schemas.message import SendMessageRequest, MessageResponse
from schemas.user import UserSearchResponse, OnlineStatusRequest, OnlineStatusResponse
from services.redis_service import RedisService

router = APIRouter()

@router.get("/conversations")
async def get_conversations(user: dict = Depends(verify_token)):
    """Get all conversations for the authenticated user"""
    try:
        user_id = user["id"]
        db = get_database()
        
        # Find conversations
        cursor = db.conversations.find({
            "participants": ObjectId(user_id)
        }).sort("lastMessageAt", -1)
        
        conversations = await cursor.to_list(length=None)
        
        formatted_conversations = []
        for conv in conversations:
            # Get other participant
            other_participant_id = next(
                (str(p) for p in conv["participants"] if str(p) != user_id),
                None
            )
            
            if not other_participant_id:
                continue
            
            # Get participant details
            participant = await db.users.find_one(
                {"_id": ObjectId(other_participant_id)},
                {"firstName": 1, "lastName": 1, "picturePath": 1}
            )
            
            if not participant:
                continue
            
            # Get online status
            is_online = await RedisService.is_user_online(other_participant_id)
            
            # Get last message
            last_message = None
            if conv.get("lastMessage"):
                last_msg = await db.messages.find_one({"_id": conv["lastMessage"]})
                if last_msg:
                    last_message = {
                        "_id": str(last_msg["_id"]),
                        "content": last_msg["content"],
                        "createdAt": last_msg["createdAt"].isoformat()
                    }
            
            # Get unread count
            unread_count = await RedisService.get_unread_count(user_id, str(conv["_id"]))
            
            formatted_conversations.append({
                "_id": str(conv["_id"]),
                "participant": {
                    "_id": str(participant["_id"]),
                    "firstName": participant["firstName"],
                    "lastName": participant["lastName"],
                    "picturePath": participant.get("picturePath", ""),
                    "isOnline": is_online
                },
                "lastMessage": last_message,
                "lastMessageAt": conv["lastMessageAt"].isoformat() if conv.get("lastMessageAt") else None,
                "unreadCount": unread_count
            })
        
        return formatted_conversations
        
    except Exception as e:
        print(f"Error fetching conversations: {e}")
        return []

@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    user: dict = Depends(verify_token)
):
    """Get messages for a conversation"""
    try:
        user_id = user["id"]
        db = get_database()
        
        # Verify user is part of conversation
        conversation = await db.conversations.find_one({
            "_id": ObjectId(conversation_id),
            "participants": ObjectId(user_id)
        })
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Try cache for first page
        if page == 1:
            cached_messages = await RedisService.get_cached_messages(conversation_id)
            if cached_messages:
                print("📦 Serving messages from Redis cache")
                return {
                    "messages": cached_messages,
                    "totalPages": 1,
                    "currentPage": 1,
                    "fromCache": True
                }
        
        # Fetch from MongoDB
        print("📊 Serving messages from MongoDB")
        cursor = db.messages.find({
            "conversationId": ObjectId(conversation_id)
        }).sort("createdAt", -1).skip((page - 1) * limit).limit(limit)
        
        messages = await cursor.to_list(length=limit)
        
        # Get sender details for each message
        formatted_messages = []
        for msg in messages:
            sender = await db.users.find_one(
                {"_id": msg["sender"]},
                {"firstName": 1, "lastName": 1, "picturePath": 1}
            )
            
            if sender:
                formatted_messages.append({
                    "_id": str(msg["_id"]),
                    "conversationId": str(msg["conversationId"]),
                    "sender": {
                        "_id": str(sender["_id"]),
                        "firstName": sender["firstName"],
                        "lastName": sender["lastName"],
                        "picturePath": sender.get("picturePath", "")
                    },
                    "content": msg["content"],
                    "read": msg.get("read", False),
                    "readAt": msg.get("readAt").isoformat() if msg.get("readAt") else None,
                    "createdAt": msg["createdAt"].isoformat()
                })
        
        # Cache first page
        if page == 1 and formatted_messages:
            for msg in reversed(formatted_messages[:50]):
                await RedisService.cache_message(conversation_id, msg)
        
        total = await db.messages.count_documents({"conversationId": ObjectId(conversation_id)})
        
        return {
            "messages": list(reversed(formatted_messages)),
            "totalPages": (total + limit - 1) // limit,
            "currentPage": page,
            "fromCache": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch messages")

@router.post("/messages")
async def send_message(
    request: SendMessageRequest,
    user: dict = Depends(verify_token)
):
    """Send a message (REST endpoint)"""
    try:
        sender_id = user["id"]
        recipient_id = request.recipientId
        content = request.content.strip()
        
        if not content:
            raise HTTPException(status_code=400, detail="Message content required")
        
        db = get_database()
        
        # Get or create conversation
        conversation = await db.conversations.find_one({
            "participants": {"$all": [ObjectId(sender_id), ObjectId(recipient_id)]}
        })
        
        if not conversation:
            conversation = {
                "participants": [ObjectId(sender_id), ObjectId(recipient_id)],
                "lastMessage": None,
                "lastMessageAt": datetime.utcnow(),
                "unreadCount": {sender_id: 0, recipient_id: 0},
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
            result = await db.conversations.insert_one(conversation)
            conversation["_id"] = result.inserted_id
        
        # Create message
        message = {
            "conversationId": conversation["_id"],
            "sender": ObjectId(sender_id),
            "content": content,
            "read": False,
            "readAt": None,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        result = await db.messages.insert_one(message)
        message["_id"] = result.inserted_id
        
        # Update conversation
        unread_count = conversation.get("unreadCount", {})
        unread_count[recipient_id] = unread_count.get(recipient_id, 0) + 1
        
        await db.conversations.update_one(
            {"_id": conversation["_id"]},
            {
                "$set": {
                    "lastMessage": message["_id"],
                    "lastMessageAt": datetime.utcnow(),
                    "unreadCount": unread_count
                }
            }
        )
        
        # Get sender info
        sender = await db.users.find_one(
            {"_id": ObjectId(sender_id)},
            {"firstName": 1, "lastName": 1, "picturePath": 1}
        )
        
        # Cache and increment unread
        message_obj = {
            "_id": str(message["_id"]),
            "conversationId": str(conversation["_id"]),
            "sender": {
                "_id": str(sender["_id"]),
                "firstName": sender["firstName"],
                "lastName": sender["lastName"],
                "picturePath": sender.get("picturePath", "")
            },
            "content": content,
            "createdAt": message["createdAt"].isoformat(),
            "read": False
        }
        
        await RedisService.cache_message(str(conversation["_id"]), message_obj)
        await RedisService.increment_unread(recipient_id, str(conversation["_id"]))
        
        return message_obj
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@router.patch("/conversations/{conversation_id}/read")
async def mark_as_read(
    conversation_id: str,
    user: dict = Depends(verify_token)
):
    """Mark messages as read"""
    try:
        user_id = user["id"]
        db = get_database()
        
        # Update messages
        await db.messages.update_many(
            {
                "conversationId": ObjectId(conversation_id),
                "sender": {"$ne": ObjectId(user_id)},
                "read": False
            },
            {
                "$set": {
                    "read": True,
                    "readAt": datetime.utcnow()
                }
            }
        )
        
        # Update conversation
        await db.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": {f"unreadCount.{user_id}": 0}}
        )
        
        # Reset Redis unread count
        await RedisService.reset_unread(user_id, conversation_id)
        
        return {"message": "Messages marked as read"}
        
    except Exception as e:
        print(f"Error marking messages as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark messages as read")

@router.get("/users/search", response_model=List[UserSearchResponse])
async def search_users(
    query: str = Query(..., min_length=2),
    user: dict = Depends(verify_token)
):
    """Search for users"""
    try:
        user_id = user["id"]
        db = get_database()
        
        # Search users
        cursor = db.users.find({
            "_id": {"$ne": ObjectId(user_id)},
            "$or": [
                {"firstName": {"$regex": query, "$options": "i"}},
                {"lastName": {"$regex": query, "$options": "i"}}
            ]
        }).limit(10)
        
        users = await cursor.to_list(length=10)
        
        # Add online status
        users_with_status = []
        for u in users:
            is_online = await RedisService.is_user_online(str(u["_id"]))
            users_with_status.append({
                "id": str(u["_id"]),
                "firstName": u["firstName"],
                "lastName": u["lastName"],
                "picturePath": u.get("picturePath", ""),
                "isOnline": is_online
            })
        
        return users_with_status
        
    except Exception as e:
        print(f"Error searching users: {e}")
        raise HTTPException(status_code=500, detail="Failed to search users")

@router.post("/users/status", response_model=OnlineStatusResponse)
async def get_online_status(
    request: OnlineStatusRequest,
    user: dict = Depends(verify_token)
):
    """Get online status for multiple users"""
    try:
        if not isinstance(request.userIds, list):
            raise HTTPException(status_code=400, detail="userIds must be an array")
        
        online_users = await RedisService.get_online_friends(request.userIds)
        
        return {"onlineUsers": online_users}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting online status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get online status")