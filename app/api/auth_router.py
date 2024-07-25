from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import  OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.security import authenticate_user, create_access_token, get_user, get_password_hash, oauth2_scheme
from app.models.user_model import User as UserModel, UserProfile
from app.models.streak_model import Streak
from app.database import get_db
from app.schemas.user_schema import SignupUser

router = APIRouter(tags=["Authentication"])


@router.post("/signup")
def signup_user(user_details: SignupUser, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.email == user_details.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user_details.password)
    new_user = UserModel(full_name=user_details.full_name, email=user_details.email, hashed_password=hashed_password, is_active=True)
    new_user.streak = Streak()
    new_user.profile = UserProfile()
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@router.post("/signin")
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail= "Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        user,  # Assuming the identification is by email
    )
        # Set a secure cookie with the access token
    # response.set_cookie(
    #     key="access_token",
    #     value=access_token,
    #     httponly=True,  # Important: makes the cookie inaccessible to client-side scripts, mitigating XSS attacks
    #     max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Cookie expiration in seconds
    #     path='/',  # Cookie is valid across the entire domain
    # )
    return {"access_token": access_token, "token_type": "bearer"}

# Assuming there's a need for getting the current user
@router.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_user(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user.profile


