from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import EmailStr
from app.models.user_model import User as UserModel, UserProfile
from app.schemas.user_schema import UserProfileUpdate
from app.database import get_db
from app.security import get_user

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
