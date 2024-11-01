from datetime import date, timedelta, datetime
import json
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
        if streak.last_activity and streak.last_activity.date() == today - timedelta(days=1):
            streak.current_streak += 1
        elif not streak.last_activity or streak.last_activity.date() < today - timedelta(days=1):
            streak.current_streak = 1

        # Check if the week needs to be reset
        if not streak.last_activity or streak.last_activity.weekday() > today.weekday():  # Assumes the week starts on Monday
            streak.week = json.dumps({ "Mon": False, "Tue": False, "Wed": False,
                                       "Thu": False, "Fri": False, "Sat": False, "Sun": False })

        # Update the week dictionary
        week_data = json.loads(streak.week)
        week_data[today.strftime('%a')[:3]] = True
        streak.week = json.dumps(week_data)

        streak.last_activity = today

        if streak.current_streak > streak.longest_streak:
            streak.longest_streak = streak.current_streak
    else:
        streak = Streak(user_id=user.id, current_streak=1, longest_streak=1, last_activity=today, week=json.dumps({ "Mon": False, "Tue": False, "Wed": False, "Thu": False, "Fri": False, "Sat": False, "Sun": False }))
        week_data = json.loads(streak.week)
        week_data[today.strftime('%a')[:3]] = True
        streak.week = json.dumps(week_data)
        db.add(streak)

    db.commit()
    return streak
