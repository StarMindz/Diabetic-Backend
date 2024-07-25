from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import EmailStr
from app.database import get_db
from app.utilities.streak import update_streak
from app.security import oauth2_scheme, get_user
from app.models.user_model import User
from app.models.streak_model import Streak
from app.schemas.streak_schema import StreakResponse

router = APIRouter(tags=["Streak"])

@router.post("/set_streak")
def set_streak(user_email: EmailStr, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # Assume scanning logic here
    # Update the user's streak
    if (user_email != get_user(db, token).email):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this user's streak")
    streak = update_streak(user_email, db)
    return {"message": "Food scanned successfully", "streak": streak.current_streak}

@router.get("/get_streak", response_model=StreakResponse)
def get_streak(user_email: EmailStr, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    if (user_email != get_user(db, token).email):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this user's streak")
    
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    streak = db.query(Streak).filter(Streak.user_id == user.id).first()
    if not streak:
        raise HTTPException(status_code=404, detail="Streak record not found")
    return streak