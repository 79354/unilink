from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # MongoDB
    MONGO_URL: str
    
    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    
    # AWS S3
    AWS_REGION: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_S3_BUCKET_NAME: str
    
    # Email
    EMAIL_USER: str
    EMAIL_PASSWORD: str
    
    # Google Gemini
    GEMINI_API_KEY: str
    
    # Discord OAuth
    DISCORD_CLIENT_ID: str
    DISCORD_CLIENT_SECRET: str
    DISCORD_REDIRECT_URI: str
    
    # App
    CLIENT_URL: str = "http://localhost:3000"
    SESSION_SECRET: str
    PORT: int = 3001
    
    class Config:
        env_file = ".env"

settings = Settings()