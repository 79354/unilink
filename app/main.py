from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.core.database import init_db, close_db
from app.core.redis_client import init_redis, close_redis
from app.api import auth, users, posts, s3, otp, captions

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await init_redis()
    print("✅ MongoDB and Redis connected")
    yield
    # Shutdown
    await close_db()
    await close_redis()
    print("👋 Connections closed")

app = FastAPI(title="UniLink API", lifespan=lifespan)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CLIENT_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (for backward compatibility)
if os.path.exists("public/assets"):
    app.mount("/assets", StaticFiles(directory="public/assets"), name="assets")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(posts.router, prefix="/posts", tags=["posts"])
app.include_router(s3.router, prefix="/s3", tags=["s3"])
app.include_router(otp.router, prefix="/otp", tags=["otp"])
app.include_router(captions.router, prefix="/captions", tags=["captions"])

@app.get("/")
async def root():
    return {"message": "🚀 UniLink API is running"}
