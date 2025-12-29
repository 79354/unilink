from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.core.database import get_database
from app.core.security import hash_password
from app.utils.email_service import generate_otp, send_otp_email
from bson import ObjectId
import random

router = APIRouter()

class SendOTPRequest(BaseModel):
    email: EmailStr
    firstName: str
    lastName: str
    password: str
    picturePath: str = ""
    location: str = ""
    Year: str = ""

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str

class ResendOTPRequest(BaseModel):
    email: EmailStr

@router.post("/send")
async def send_otp(request: SendOTPRequest):
    try:
        db = get_database()
        users_collection = db.users
        otp_collection = db.otps
        
        # Check if user exists
        existing_user = await users_collection.find_one({"email": request.email.lower()})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Generate OTP
        otp = generate_otp()
        print(f"🔐 Generated OTP for {request.email}: {otp}")
        
        # Hash password
        hashed_password = hash_password(request.password)
        
        # Delete existing OTP
        await otp_collection.delete_many({"email": request.email.lower()})
        
        # Store OTP
        otp_doc = {
            "email": request.email.lower(),
            "otp": otp,
            "userData": {
                "firstName": request.firstName,
                "lastName": request.lastName,
                "email": request.email.lower(),
                "password": hashed_password,
                "picturePath": request.picturePath,
                "location": request.location,
                "Year": request.Year
            },
            "attempts": 0
        }
        
        await otp_collection.insert_one(otp_doc)
        
        # Send email
        await send_otp_email(request.email, otp, request.firstName)
        
        return {"message": "OTP sent successfully", "email": request.email}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error sending OTP: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {str(e)}")

@router.post("/verify")
async def verify_otp(request: VerifyOTPRequest):
    try:
        db = get_database()
        users_collection = db.users
        otp_collection = db.otps
        
        # Find OTP document
        otp_doc = await otp_collection.find_one({"email": request.email.lower()})
        
        if not otp_doc:
            raise HTTPException(status_code=400, detail="OTP expired or not found")
        
        if otp_doc["attempts"] >= 5:
            await otp_collection.delete_one({"email": request.email.lower()})
            raise HTTPException(status_code=400, detail="Too many failed attempts")
        
        if otp_doc["otp"] != request.otp:
            await otp_collection.update_one(
                {"email": request.email.lower()},
                {"$inc": {"attempts": 1}}
            )
            raise HTTPException(
                status_code=400,
                detail=f"Invalid OTP. Attempts left: {5 - otp_doc['attempts'] - 1}"
            )
        
        # Create user
        user_data = otp_doc["userData"]
        new_user = {
            "firstName": user_data["firstName"],
            "lastName": user_data["lastName"],
            "email": user_data["email"],
            "password": user_data["password"],
            "picturePath": user_data["picturePath"],
            "location": user_data["location"],
            "Year": user_data["Year"],
            "friends": [],
            "viewedProfile": random.randint(0, 10000),
            "impressions": random.randint(0, 10000),
            "provider": "local",
            "twitterUrl": "",
            "linkedInUrl": ""
        }
        
        result = await users_collection.insert_one(new_user)
        await otp_collection.delete_one({"email": request.email.lower()})
        
        # Get created user
        created_user = await users_collection.find_one({"_id": result.inserted_id})
        created_user.pop("password", None)
        created_user["_id"] = str(created_user["_id"])
        
        return {
            "message": "Account created successfully",
            "user": created_user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error verifying OTP: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to verify OTP: {str(e)}")

@router.post("/resend")
async def resend_otp(request: ResendOTPRequest):
    try:
        db = get_database()
        otp_collection = db.otps
        
        # Find OTP document
        otp_doc = await otp_collection.find_one({"email": request.email.lower()})
        
        if not otp_doc:
            raise HTTPException(status_code=400, detail="No pending verification found")
        
        # Generate new OTP
        new_otp = generate_otp()
        print(f"🔐 Resent OTP for {request.email}: {new_otp}")
        
        # Update OTP
        await otp_collection.update_one(
            {"email": request.email.lower()},
            {"$set": {"otp": new_otp, "attempts": 0}}
        )
        
        # Send email
        await send_otp_email(
            request.email,
            new_otp,
            otp_doc["userData"]["firstName"]
        )
        
        return {"message": "OTP resent successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error resending OTP: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to resend OTP: {str(e)}")