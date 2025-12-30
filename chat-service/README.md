# Chat Service

A real-time chat microservice built with FastAPI, Redis, WebSockets, and Socket.IO.  
Designed for scalable, low-latency messaging with authentication and cross-server communication.

---

## Project Structure

chat-service/
  Dockerfile
  pyproject.toml
  main.py

  config/
    __init__.py
    settings.py

  core/
    __init__.py
    redis_client.py
    database.py

  middleware/
    __init__.py
    auth.py

  models/
    __init__.py
    user.py
    message.py
    conversation.py

  schemas/
    __init__.py
    message.py
    user.py

  routes/
    __init__.py
    chat.py

  services/
    __init__.py
    redis_service.py
    socket_service.py

  websocket/
    __init__.py
    manager.py

---

## Key Features

- **JWT Authentication**
  - Secures both REST APIs and WebSocket connections.

- **Real-Time Messaging**
  - Implemented using Socket.IO for low-latency, bidirectional communication.

- **Redis Integration**
  - Message caching for faster access.
  - Online/offline user presence tracking.
  - Pub/Sub for cross-instance event propagation.

- **Chat Capabilities**
  - Typing indicators
  - Read receipts
  - Unread message counts
  - Conversation-based messaging

---

## Tech Stack

- **FastAPI** – REST APIs and WebSocket handling  
- **Socket.IO** – Real-time messaging layer  
- **Redis** – Caching, Pub/Sub, presence tracking  
- **MongoDB** – Persistent message and user storage  
- **JWT** – Authentication and authorization  

---

## Usage Notes

- Designed to run as a standalone microservice.
- Supports horizontal scaling using Redis Pub/Sub.
- WebSocket authentication reuses JWT issued by the auth service.
