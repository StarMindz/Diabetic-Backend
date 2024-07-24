from datetime import date, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.streak_model import Streak
from app.models.user_model import User

def update_streak(email: str, db: Session):
    # Retrieve the user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")  # Or handle more appropriately based on your error handling strategy

    # Access the user's streak or create a new one if it does not exist
    streak = db.query(Streak).filter(Streak.user_id == user.id).first()
    today = date.today()

    if streak:
        if streak.last_activity == today - timedelta(days=1):
            streak.current_streak += 1
        elif streak.last_activity < today - timedelta(days=1):
            streak.current_streak = 1

        if streak.current_streak > streak.longest_streak:
            streak.longest_streak = streak.current_streak

        streak.last_activity = today
    else:
        streak = Streak(user_id=user.id, current_streak=1, longest_streak=1, last_activity=today)
        db.add(streak)

    db.commit()
    return streak
