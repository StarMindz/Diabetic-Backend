from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from pydantic import EmailStr
from app.models.user_model import User as UserModel, UserProfile
from app.schemas.user_schema import UserProfileUpdate
from app.database import get_db
from app.security import get_user
from dotenv import load_dotenv
from PIL import Image
import os
import io
import boto3
from botocore.exceptions import NoCredentialsError

router = APIRouter(tags=["Users"])

# @router.post("/users/")
# def create_user(email: str, password: str, db: Session = Depends(get_db)):
#     db_user = db.query(UserModel).filter(UserModel.email == email).first()
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     hashed_password = get_password_hash(password)
#     db_user = UserModel(email=email, hashed_password=hashed_password, is_active=True)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user

load_dotenv()

# Configure s3 bucket
BUCKET_NAME = os.environ["BUCKET_NAME"]
ACCESS_KEY = os.environ["ACCESS_KEY"]
SECRET_ACCESS_KEY = os.environ["SECRET_ACCESS_KEY"]
REGION = os.environ["REGION"]
S3_BASE_URL = f'https://{BUCKET_NAME}.s3.amazonaws.com/'

# Initialize the S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_ACCESS_KEY,
    region_name=REGION
)
S3_BASE_URL = f'https://{BUCKET_NAME}.s3.amazonaws.com/'

def upload_to_s3(file_path: str, bucket_name: str, object_name: str):
    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
        return f"{S3_BASE_URL}{object_name}"
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except NoCredentialsError:
        raise HTTPException(status_code=403, detail="Credentials not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{email}")
def read_user(email: str, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.email == email).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/users/profile")
def update_user_profile(profile_data: UserProfileUpdate, db: Session = Depends(get_db), user:dict = Depends(get_user)):
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.profile:
        user.profile = UserProfile()
        db.add(user.profile)

    for key, value in profile_data.dict().items():
        if value is not None:  # This checks if the provided field value is not None, preventing overwriting with None
            setattr(user.profile, key, value)

    db.commit()
    db.refresh(user)

    return {
        "message": "User profile updated successfully",
        "profile": user.profile
    }

@router.put("/users/profile/image")
async def update_user_image(file: UploadFile = File(...), db: Session = Depends(get_db), user: dict = Depends(get_user)):
    mime_type = file.content_type
    file_extension = mime_type.split('/')[-1]
    image = Image.open(io.BytesIO(await file.read()))
    file_path = f"temp_image2.{file_extension}"
    image.save(file_path)
    filename = user.email.split("@")[0]
    s3_key = f"Avatar/{filename}.{file_extension}"
    s3_url = upload_to_s3(file_path, BUCKET_NAME, s3_key)

    user.profile.image = s3_url

    db.commit()
    db.refresh(user)

    return {
        "message": "User profile image updated successfully",
        "image_url": s3_url
    }
