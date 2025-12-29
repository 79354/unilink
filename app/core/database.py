from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client: AsyncIOMotorClient = None
database = None

async def init_db():
    global client, database
    client = AsyncIOMotorClient(settings.MONGO_URL)
    database = client.get_database()
    print("✅ MongoDB connected")

async def close_db():
    global client
    if client:
        client.close()

def get_database():
    return database