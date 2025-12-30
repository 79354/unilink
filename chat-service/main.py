from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import socketio

from config.settings import settings
from core.database import connect_to_mongo, close_mongo_connection
from core.redis_client import connect_to_redis, close_redis_connection
from routes import chat
from websocket.manager import sio
from services.socket_service import initialize_socket_handlers

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    await connect_to_redis()
    initialize_socket_handlers(sio)
    print("Chat Service - MongoDB connected")
    print("Chat Service running on port 4000")
    print("WebSocket ready for connections")
    yield
    # Shutdown
    await close_mongo_connection()
    await close_redis_connection()

app = FastAPI(title="Chat Service", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.MAIN_APP_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Socket.IO
socket_app = socketio.ASGIApp(
    sio,
    other_asgi_app=app,
    socketio_path="socket.io"
)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "OK", "service": "chat-service"}

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

# Export for uvicorn
app = socket_app