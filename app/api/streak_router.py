from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import EmailStr
from app.database import get_db
from app.utilities.streak import update_streak
from app.security import  get_user
from app.models.user_model import User
from app.models.streak_model import Streak
from app.schemas.streak_schema import StreakResponse

router = APIRouter(tags=["Streak"])

@router.post("/set_streak")
def set_streak(db: Session = Depends(get_db), user:dict = Depends(get_user)):
    # Assume scanning logic here
    # Update the user's streak
    streak = update_streak(user.email, db)
    return {"message": "Streak updated successfully", "streak": streak.current_streak}

@router.get("/get_streak", response_model=StreakResponse)
def get_streak(db: Session = Depends(get_db), user:dict = Depends(get_user)):
    streak = db.query(Streak).filter(Streak.user_id == user.id).first()
    if not streak:
        raise HTTPException(status_code=404, detail="Streak record not found")
    return streak