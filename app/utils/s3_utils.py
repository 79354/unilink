import boto3
from botocore.config import Config
from app.core.config import settings
import secrets
from datetime import datetime

# Configure S3 client
s3_client = boto3.client(
    's3',
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    config=Config(signature_version='s3v4')
)

def generate_file_name(file_type: str) -> str:
    """Generate unique file name"""
    timestamp = int(datetime.now().timestamp() * 1000)
    random_string = secrets.token_hex(8)
    extension = file_type.split('/')[-1]
    return f"{timestamp}-{random_string}.{extension}"

async def generate_presigned_url(file_type: str, folder: str = "uploads"):
    """Generate presigned URL for upload"""
    try:
        file_name = generate_file_name(file_type)
        key = f"{folder}/{file_name}"
        
        # Generate presigned URL for PUT
        upload_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': settings.AWS_S3_BUCKET_NAME,
                'Key': key,
                'ContentType': file_type
            },
            ExpiresIn=300  # 5 minutes
        )
        
        # Generate public access URL
        access_url = f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
        
        return {
            "uploadUrl": upload_url,
            "key": key,
            "accessUrl": access_url
        }
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        raise

async def delete_file_from_s3(key: str):
    """Delete file from S3"""
    try:
        s3_client.delete_object(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=key
        )
        print(f"File deleted successfully: {key}")
        return True
    except Exception as e:
        print(f"Error deleting file from S3: {e}")
        raise
