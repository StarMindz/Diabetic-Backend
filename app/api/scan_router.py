from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import EmailStr
from app.database import get_db
from app.utilities.streak import update_streak
from app.security import oauth2_scheme

router = APIRouter(tags=["Scan"])

@router.post("/scan-food")
def scan_food(user_email: EmailStr, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # Assume scanning logic here
    # Update the user's streak
    streak = update_streak(user_email, db)
    return {"message": "Food scanned successfully", "streak": streak.current_streak}
