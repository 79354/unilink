from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from app.models.user import UserCreate, UserResponse, UserInDB
from app.core.database import get_database
from app.core.security import hash_password, verify_password, create_access_token
from pydantic import BaseModel, EmailStr
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from app.core.config import settings
import random

router = APIRouter()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    token: str
    user: UserResponse

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    db = get_database()
    users_collection = db.users
    
    # Check if user exists
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user document
    new_user = {
        "firstName": user_data.firstName,
        "lastName": user_data.lastName,
        "email": user_data.email,
        "password": hashed_password,
        "picturePath": user_data.picturePath or "",
        "friends": [],
        "location": user_data.location or "",
        "Year": user_data.Year or "",
        "viewedProfile": random.randint(0, 10000),
        "impressions": random.randint(0, 10000),
        "provider": "local",
        "twitterUrl": "",
        "linkedInUrl": "",
    }
    
    result = await users_collection.insert_one(new_user)
    created_user = await users_collection.find_one({"_id": result.inserted_id})
    
    # Convert to response format
    created_user["_id"] = str(created_user["_id"])
    return created_user

@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    db = get_database()
    users_collection = db.users
    
    # Find user
    user = await users_collection.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(status_code=400, detail="User does not exist")
    
    # Verify password
    if not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # Create token
    token = create_access_token({"id": str(user["_id"])})
    
    # Remove password from response
    user.pop("password", None)
    user["_id"] = str(user["_id"])
    
    return {"token": token, "user": user}

# Discord OAuth setup
oauth = OAuth()
oauth.register(
    name='discord',
    client_id=settings.DISCORD_CLIENT_ID,
    client_secret=settings.DISCORD_CLIENT_SECRET,
    authorize_url='https://discord.com/api/oauth2/authorize',
    access_token_url='https://discord.com/api/oauth2/token',
    client_kwargs={'scope': 'identify email guilds'}
)

@router.get("/discord")
async def discord_login(request: Request):
    redirect_uri = settings.DISCORD_REDIRECT_URI
    return await oauth.discord.authorize_redirect(request, redirect_uri)

@router.get("/discord/callback")
async def discord_callback(request: Request):
    try:
        token = await oauth.discord.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            # Fetch user info manually
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    'https://discord.com/api/users/@me',
                    headers={'Authorization': f'Bearer {token["access_token"]}'}
                )
                user_info = response.json()
        
        db = get_database()
        users_collection = db.users
        
        # Check if user exists by Discord ID
        user = await users_collection.find_one({"discordId": user_info["id"]})
        
        if not user and user_info.get("email"):
            # Check by email
            user = await users_collection.find_one({"email": user_info["email"]})
            if user:
                # Link Discord account
                await users_collection.update_one(
                    {"_id": user["_id"]},
                    {"$set": {
                        "discordId": user_info["id"],
                        "provider": "discord",
                        "discordUsername": user_info["username"],
                        "discordAvatar": user_info.get("avatar", "")
                    }}
                )
        
        if not user:
            # Create new user
            new_user = {
                "discordId": user_info["id"],
                "provider": "discord",
                "email": user_info.get("email", f"{user_info['id']}@discord.temp"),
                "firstName": user_info["username"],
                "lastName": user_info["username"],
                "discordUsername": user_info["username"],
                "discordAvatar": user_info.get("avatar", ""),
                "picturePath": f"https://cdn.discordapp.com/avatars/{user_info['id']}/{user_info['avatar']}.png" if user_info.get("avatar") else "",
                "friends": [],
                "location": "",
                "Year": "",
                "viewedProfile": 0,
                "impressions": 0,
                "twitterUrl": "",
                "linkedInUrl": "",
                "password": ""  # No password for OAuth users
            }
            result = await users_collection.insert_one(new_user)
            user = await users_collection.find_one({"_id": result.inserted_id})
        
        # Generate JWT
        jwt_token = create_access_token({"id": str(user["_id"])})
        
        # Remove password
        user.pop("password", None)
        user["_id"] = str(user["_id"])
        
        # Redirect to frontend with token and user data
        import urllib.parse
        user_data = urllib.parse.quote(str(user))
        redirect_url = f"{settings.CLIENT_URL}/auth/callback?token={jwt_token}&user={user_data}"
        
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        print(f"❌ Error in Discord callback: {e}")
        return RedirectResponse(url=f"{settings.CLIENT_URL}/?error=server_error")
