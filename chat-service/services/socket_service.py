import asyncio
import json
from datetime import datetime
from bson import ObjectId
from core.database import get_database
from core.redis_client import get_redis_sub
from services.redis_service import RedisService, REDIS_CHANNELS, NOTIFICATION_CHANNELS

async def publish_message_notification(recipient_id, sender_id, sender_name, sender_picture, content, conversation_id):
    """Publish message notification to notification service"""
    try:
        await RedisService.publish(NOTIFICATION_CHANNELS.MESSAGE, {
            "userId": recipient_id,
            "actorId": sender_id,
            "actorName": sender_name,
            "actorPicture": sender_picture,
            "relatedId": conversation_id,
            "metadata": {
                "messagePreview": content[:50]
            }
        })
        print(f"Published message notification for user {recipient_id}")
    except Exception as e:
        print(f"Error publishing message notification: {e}")

async def get_or_create_conversation(user_id1: str, user_id2: str):
    """Get or create conversation between two users"""
    db = get_database()
    
    conversation = await db.conversations.find_one({
        "participants": {"$all": [ObjectId(user_id1), ObjectId(user_id2)]}
    })
    
    if not conversation:
        conversation = {
            "participants": [ObjectId(user_id1), ObjectId(user_id2)],
            "lastMessage": None,
            "lastMessageAt": datetime.utcnow(),
            "unreadCount": {user_id1: 0, user_id2: 0},
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        result = await db.conversations.insert_one(conversation)
        conversation["_id"] = result.inserted_id
    
    return conversation

async def get_user_info(user_id: str):
    """Get user information"""
    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user:
        return {
            "_id": str(user["_id"]),
            "firstName": user["firstName"],
            "lastName": user["lastName"],
            "picturePath": user.get("picturePath", "")
        }
    return None

async def get_user_with_friends(user_id: str):
    """Get user with friends list"""
    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(user_id)}, {"friends": 1})
    return user

async def mark_messages_as_read(sio, user_id: str, conversation_id: str):
    """Mark messages as read"""
    try:
        db = get_database()
        
        result = await db.messages.update_many(
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
        
        if result.modified_count > 0:
            print(f"Marked {result.modified_count} messages as read")
        
        # Update conversation
        await db.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": {f"unreadCount.{user_id}": 0}}
        )
        
        # Reset Redis unread count
        await RedisService.reset_unread(user_id, conversation_id)
        
        # Get and emit updated total unread count
        total_unread = await RedisService.get_total_unread(user_id)
        await sio.emit('unread:total', {'count': total_unread}, room=user_id)
        
        # Notify other participants
        await RedisService.publish(REDIS_CHANNELS.MESSAGE_READ, {
            "conversationId": conversation_id,
            "userId": user_id
        })
        
    except Exception as e:
        print(f"Error marking messages as read: {e}")

async def stop_typing(socket_id: str, user_id: str, conversation_id: str):
    """Stop typing indicator"""
    try:
        await RedisService.remove_typing(conversation_id, user_id)
        await RedisService.publish(REDIS_CHANNELS.TYPING_STOP, {
            "conversationId": conversation_id,
            "userId": user_id,
            "socketId": socket_id
        })
    except Exception as e:
        print(f"Error stopping typing: {e}")

def initialize_socket_handlers(sio):
    """Initialize Socket.IO event handlers"""
    
    # Subscribe to Redis Pub/Sub channels
    async def subscribe_to_channels():
        redis_sub = get_redis_sub()
        pubsub = redis_sub.pubsub()
        
        await pubsub.subscribe(
            REDIS_CHANNELS.MESSAGE_NEW,
            REDIS_CHANNELS.TYPING_START,
            REDIS_CHANNELS.TYPING_STOP,
            REDIS_CHANNELS.USER_ONLINE,
            REDIS_CHANNELS.USER_OFFLINE,
            REDIS_CHANNELS.MESSAGE_READ
        )
        
        async for message in pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                channel = message['channel']
                
                if channel == REDIS_CHANNELS.MESSAGE_NEW:
                    await sio.emit('message:new', {
                        'message': data['message'],
                        'conversationId': data['conversationId']
                    }, room=data['conversationId'])
                
                elif channel == REDIS_CHANNELS.TYPING_START:
                    await sio.emit('typing:start', {
                        'conversationId': data['conversationId'],
                        'userId': data['userId'],
                        'user': data['user']
                    }, room=data['conversationId'])
                
                elif channel == REDIS_CHANNELS.TYPING_STOP:
                    await sio.emit('typing:stop', {
                        'conversationId': data['conversationId'],
                        'userId': data['userId']
                    }, room=data['conversationId'])
                
                elif channel == REDIS_CHANNELS.USER_ONLINE:
                    await sio.emit('user:online', {'userId': data['userId']})
                
                elif channel == REDIS_CHANNELS.USER_OFFLINE:
                    await sio.emit('user:offline', {'userId': data['userId']})
                
                elif channel == REDIS_CHANNELS.MESSAGE_READ:
                    await sio.emit('messages:read', {
                        'conversationId': data['conversationId'],
                        'userId': data['userId']
                    }, room=data['conversationId'])
    
    asyncio.create_task(subscribe_to_channels())
    
    @sio.event
    async def connect(sid, environ, auth):
        """Handle connection"""
        async with sio.session(sid) as session:
            user_id = session.get('user_id')
            if not user_id:
                return
            
            print(f"User connected: {user_id}, Socket ID: {sid}")
            
            try:
                await RedisService.set_user_socket(user_id, sid)
                await RedisService.set_user_online(user_id)
                
                # Join user room
                sio.enter_room(sid, user_id)
                
                # Publish online status
                await RedisService.publish(REDIS_CHANNELS.USER_ONLINE, {"userId": user_id})
                
                # Send online friends
                user = await get_user_with_friends(user_id)
                if user and user.get('friends'):
                    friend_ids = [str(f) for f in user['friends']]
                    online_friends = await RedisService.get_online_friends(friend_ids)
                    await sio.emit('friends:online', {'userIds': online_friends}, room=sid)
                
                # Send total unread count
                total_unread = await RedisService.get_total_unread(user_id)
                await sio.emit('unread:total', {'count': total_unread}, room=sid)
                
            except Exception as e:
                print(f"Error on connection: {e}")
    
    @sio.event
    async def disconnect(sid):
        """Handle disconnection"""
        async with sio.session(sid) as session:
            user_id = session.get('user_id')
            if not user_id:
                return
            
            print(f"User disconnected: {user_id}, Socket ID: {sid}")
            
            try:
                await RedisService.remove_user_socket(user_id, sid)
                await RedisService.set_user_offline(user_id)
                await RedisService.publish(REDIS_CHANNELS.USER_OFFLINE, {"userId": user_id})
            except Exception as e:
                print(f"Error on disconnect: {e}")
    
    @sio.event
    async def conversation_join(sid, data):
        """Join conversation room"""
        async with sio.session(sid) as session:
            user_id = session.get('user_id')
            if not user_id:
                return
            
            conversation_id = data.get('conversationId')
            if not conversation_id:
                return
            
            try:
                sio.enter_room(sid, conversation_id)
                print(f"User {user_id} joined conversation {conversation_id}")
                await mark_messages_as_read(sio, user_id, conversation_id)
            except Exception as e:
                print(f"Error joining conversation: {e}")
    
    @sio.event
    async def conversation_leave(sid, data):
        """Leave conversation room"""
        async with sio.session(sid) as session:
            user_id = session.get('user_id')
            if not user_id:
                return
            
            conversation_id = data.get('conversationId')
            if not conversation_id:
                return
            
            try:
                sio.leave_room(sid, conversation_id)
                await RedisService.remove_typing(conversation_id, user_id)
                print(f"User {user_id} left conversation {conversation_id}")
            except Exception as e:
                print(f"Error leaving conversation: {e}")
    
    @sio.event
    async def message_send(sid, data):
        """Send message"""
        async with sio.session(sid) as session:
            user_id = session.get('user_id')
            if not user_id:
                return
            
            try:
                recipient_id = data.get('recipientId')
                content = data.get('content', '').strip()
                
                if not content:
                    await sio.emit('error', {'message': 'Message content required'}, room=sid)
                    return
                
                print(f"Message from {user_id} to {recipient_id}: \"{content[:30]}...\"")
                
                db = get_database()
                
                # Get or create conversation
                conversation = await get_or_create_conversation(user_id, recipient_id)
                conversation_id = str(conversation['_id'])
                
                # Create message
                message = {
                    "conversationId": conversation['_id'],
                    "sender": ObjectId(user_id),
                    "content": content,
                    "read": False,
                    "readAt": None,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                }
                result = await db.messages.insert_one(message)
                message['_id'] = result.inserted_id
                
                # Update conversation
                unread_count = conversation.get('unreadCount', {})
                unread_count[recipient_id] = unread_count.get(recipient_id, 0) + 1
                
                await db.conversations.update_one(
                    {"_id": conversation['_id']},
                    {
                        "$set": {
                            "lastMessage": message['_id'],
                            "lastMessageAt": datetime.utcnow(),
                            "unreadCount": unread_count
                        }
                    }
                )
                
                # Get sender info
                sender = await get_user_info(user_id)
                
                # Prepare message object
                message_obj = {
                    "_id": str(message['_id']),
                    "conversationId": conversation_id,
                    "sender": sender,
                    "content": content,
                    "createdAt": message['createdAt'].isoformat(),
                    "read": False
                }
                
                # Cache message
                await RedisService.cache_message(conversation_id, message_obj)
                
                # Increment unread
                await RedisService.increment_unread(recipient_id, conversation_id)
                
                # Publish message notification
                await publish_message_notification(
                    recipient_id,
                    user_id,
                    f"{sender['firstName']} {sender['lastName']}",
                    sender['picturePath'],
                    content,
                    conversation_id
                )
                
                # Publish message
                await RedisService.publish(REDIS_CHANNELS.MESSAGE_NEW, {
                    "conversationId": conversation_id,
                    "message": message_obj
                })
                
                # Stop typing
                await stop_typing(sid, user_id, conversation_id)
                
                # Update unread counts
                total_unread = await RedisService.get_total_unread(user_id)
                await sio.emit('unread:total', {'count': total_unread}, room=sid)
                
                recipient_unread = await RedisService.get_total_unread(recipient_id)
                await sio.emit('unread:total', {'count': recipient_unread}, room=recipient_id)
                
                print(f"Message sent successfully")
                
            except Exception as e:
                print(f"Error sending message: {e}")
                await sio.emit('error', {'message': 'Failed to send message'}, room=sid)
    
    @sio.event
    async def typing_start(sid, data):
        """Handle typing start"""
        async with sio.session(sid) as session:
            user_id = session.get('user_id')
            if not user_id:
                return
            
            conversation_id = data.get('conversationId')
            if not conversation_id:
                return
            
            try:
                await RedisService.set_typing(conversation_id, user_id)
                user = await get_user_info(user_id)
                
                if user:
                    await RedisService.publish(REDIS_CHANNELS.TYPING_START, {
                        "conversationId": conversation_id,
                        "userId": user_id,
                        "socketId": sid,
                        "user": {
                            "firstName": user['firstName'],
                            "lastName": user['lastName']
                        }
                    })
            except Exception as e:
                print(f"Error on typing start: {e}")
    
    @sio.event
    async def typing_stop(sid, data):
        """Handle typing stop"""
        async with sio.session(sid) as session:
            user_id = session.get('user_id')
            if not user_id:
                return
            
            conversation_id = data.get('conversationId')
            if not conversation_id:
                return
            
            await stop_typing(sid, user_id, conversation_id)
    
    @sio.event
    async def messages_read(sid, data):
        """Mark messages as read"""
        async with sio.session(sid) as session:
            user_id = session.get('user_id')
            if not user_id:
                return
            
            conversation_id = data.get('conversationId')
            if not conversation_id:
                return
            
            await mark_messages_as_read(sio, user_id, conversation_id)
    
    @sio.event
    async def users_status(sid, data):
        """Get online status"""
        async with sio.session(sid) as session:
            user_id = session.get('user_id')
            if not user_id:
                return
            
            try:
                user_ids = data.get('userIds', [])
                if not isinstance(user_ids, list):
                    await sio.emit('error', {'message': 'userIds must be an array'}, room=sid)
                    return
                
                online_users = await RedisService.get_online_friends(user_ids)
                await sio.emit('users:status', {'onlineUsers': online_users}, room=sid)
            except Exception as e:
                print(f"Error getting user status: {e}")
                await sio.emit('error', {'message': 'Failed to get user status'}, room=sid)