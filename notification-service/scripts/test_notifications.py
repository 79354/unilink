#!/usr/bin/env python3
"""
Test script for publishing notification events to Redis Pub/Sub
Simulates the main application publishing notification events
"""

import redis
import json
import time
import random
from typing import Dict, Any

# Redis connection
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    password='',  # Set if Redis has password
    decode_responses=True
)

# Notification channels
CHANNELS = {
    'like': 'notification:like',
    'message': 'notification:message',
    'profile-view': 'notification:profile-view',
    'friend-post': 'notification:friend-post',
    'friend-request': 'notification:friend-request',
}

# Sample users
USERS = ['user_123', 'user_456', 'user_789']
ACTORS = [
    {'id': 'actor_1', 'name': 'John Doe', 'picture': 'https://example.com/john.jpg'},
    {'id': 'actor_2', 'name': 'Jane Smith', 'picture': 'https://example.com/jane.jpg'},
    {'id': 'actor_3', 'name': 'Bob Wilson', 'picture': 'https://example.com/bob.jpg'},
    {'id': 'actor_4', 'name': 'Alice Brown', 'picture': 'https://example.com/alice.jpg'},
]


def publish_notification(channel: str, data: Dict[str, Any]) -> None:
    """Publish notification event to Redis channel"""
    try:
        payload = json.dumps(data)
        redis_client.publish(channel, payload)
        print(f"Published to {channel}:")
        print(f"   {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"Error publishing: {e}")


def test_like_notification():
    """Test like notification (groupable)"""
    user = random.choice(USERS)
    actor = random.choice(ACTORS)
    
    data = {
        'userId': user,
        'actorId': actor['id'],
        'actorName': actor['name'],
        'actorPicture': actor['picture'],
        'relatedId': 'post_123',
        'priority': 'medium',
        'metadata': {}
    }
    
    publish_notification(CHANNELS['like'], data)


def test_message_notification():
    """Test message notification (high priority)"""
    user = random.choice(USERS)
    actor = random.choice(ACTORS)
    
    data = {
        'userId': user,
        'actorId': actor['id'],
        'actorName': actor['name'],
        'actorPicture': actor['picture'],
        'relatedId': f'msg_{random.randint(1000, 9999)}',
        'priority': 'high',
        'metadata': {
            'messagePreview': 'Hey, how are you doing?'
        }
    }
    
    publish_notification(CHANNELS['message'], data)


def test_profile_view_notification():
    """Test profile view notification (groupable)"""
    user = random.choice(USERS)
    actor = random.choice(ACTORS)
    
    data = {
        'userId': user,
        'actorId': actor['id'],
        'actorName': actor['name'],
        'actorPicture': actor['picture'],
        'relatedId': user,
        'priority': 'low',
        'metadata': {}
    }
    
    publish_notification(CHANNELS['profile-view'], data)


def test_friend_request_notification():
    """Test friend request notification"""
    user = random.choice(USERS)
    actor = random.choice(ACTORS)
    
    data = {
        'userId': user,
        'actorId': actor['id'],
        'actorName': actor['name'],
        'actorPicture': actor['picture'],
        'relatedId': f'req_{random.randint(1000, 9999)}',
        'priority': 'high',
        'metadata': {
            'mutualFriends': 5
        }
    }
    
    publish_notification(CHANNELS['friend-request'], data)


def test_friend_post_notification():
    """Test friend post notification"""
    user = random.choice(USERS)
    actor = random.choice(ACTORS)
    
    data = {
        'userId': user,
        'actorId': actor['id'],
        'actorName': actor['name'],
        'actorPicture': actor['picture'],
        'relatedId': f'post_{random.randint(1000, 9999)}',
        'priority': 'medium',
        'metadata': {
            'postType': 'image',
            'postPreview': 'Check out my new photo!'
        }
    }
    
    publish_notification(CHANNELS['friend-post'], data)


def test_grouping():
    """Test notification grouping by sending multiple likes"""
    print("\n Testing notification grouping (multiple likes on same post)...")
    user = USERS[0]
    post_id = 'post_999'
    
    for i, actor in enumerate(ACTORS[:3], 1):
        data = {
            'userId': user,
            'actorId': actor['id'],
            'actorName': actor['name'],
            'actorPicture': actor['picture'],
            'relatedId': post_id,
            'priority': 'medium',
            'metadata': {}
        }
        
        publish_notification(CHANNELS['like'], data)
        print(f"   Sent like #{i}")
        time.sleep(1)  # Wait for grouping window


def test_all_notification_types():
    """Test all notification types"""
    print("\n Testing all notification types...")
    
    print("\n1️ Like Notification:")
    test_like_notification()
    time.sleep(1)
    
    print("\n2️ Message Notification:")
    test_message_notification()
    time.sleep(1)
    
    print("\n3️ Profile View Notification:")
    test_profile_view_notification()
    time.sleep(1)
    
    print("\n4️ Friend Request Notification:")
    test_friend_request_notification()
    time.sleep(1)
    
    print("\n5️ Friend Post Notification:")
    test_friend_post_notification()


def stress_test(count: int = 10):
    """Send multiple notifications rapidly"""
    print(f"\n⚡ Stress test: Sending {count} notifications...")
    
    notification_types = [
        test_like_notification,
        test_message_notification,
        test_profile_view_notification,
        test_friend_request_notification,
        test_friend_post_notification,
    ]
    
    for i in range(count):
        test_func = random.choice(notification_types)
        test_func()
        time.sleep(0.5)
    
    print(f"\n Sent {count} notifications")


def interactive_menu():
    """Interactive menu for testing"""
    while True:
        print("\n" + "="*50)
        print("📬 Notification Service Test Menu")
        print("="*50)
        print("1. Test Like Notification")
        print("2. Test Message Notification")
        print("3. Test Profile View Notification")
        print("4. Test Friend Request Notification")
        print("5. Test Friend Post Notification")
        print("6. Test All Notification Types")
        print("7. Test Notification Grouping")
        print("8. Stress Test (10 notifications)")
        print("9. Custom Stress Test")
        print("0. Exit")
        print("="*50)
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == '1':
            test_like_notification()
        elif choice == '2':
            test_message_notification()
        elif choice == '3':
            test_profile_view_notification()
        elif choice == '4':
            test_friend_request_notification()
        elif choice == '5':
            test_friend_post_notification()
        elif choice == '6':
            test_all_notification_types()
        elif choice == '7':
            test_grouping()
        elif choice == '8':
            stress_test(10)
        elif choice == '9':
            count = int(input("How many notifications? "))
            stress_test(count)
        elif choice == '0':
            print("\n Goodbye!")
            break
        else:
            print("\Invalid choice!")
        
        time.sleep(1)


if __name__ == '__main__':
    print("Notification Service Test Script")
    print("Connecting to Redis...")
    
    try:
        redis_client.ping()
        print("Connected to Redis successfully!")
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")
        exit(1)
    
    # Run interactive menu
    interactive_menu()