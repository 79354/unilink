from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.core.security import verify_token
from app.utils.s3_utils import generate_presigned_url
from typing import Optional

router = APIRouter()

class UploadUrlRequest(BaseModel):
    fileType: str

class UploadUrlResponse(BaseModel):
    uploadUrl: str
    key: str
    accessUrl: str

@router.post("/upload-url/profile", response_model=UploadUrlResponse)
async def get_profile_upload_url(request: UploadUrlRequest):
    """Get presigned URL for profile picture upload (NO AUTH for registration)"""
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    
    if request.fileType not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPEG, PNG, and WebP are allowed."
        )
    
    try:
        result = await generate_presigned_url(request.fileType, "profiles")
        return result
    except Exception as e:
        print(f"Error generating profile upload URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate upload URL")

@router.post("/upload-url/post", response_model=UploadUrlResponse)
async def get_post_upload_url(
    request: UploadUrlRequest,
    current_user: dict = Depends(verify_token)
):
    """Get presigned URL for post image upload (REQUIRES AUTH)"""
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    
    if request.fileType not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPEG, PNG, and WebP are allowed."
        )
    
    try:
        result = await generate_presigned_url(request.fileType, "posts")
        return result
    except Exception as e:
        print(f"Error generating post upload URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate upload URL")