from sqlalchemy import Column, Integer, DateTime, ForeignKey, JSON
from datetime import date
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from app.config import Base
import json

class Streak(Base):
    __tablename__ = "streaks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity = Column(DateTime, default=date.today())
    week = Column(JSON, default=lambda: json.dumps({ "Mon": False, "Tue": False, "Wed": False,
                                                     "Thu": False, "Fri": False, "Sat": False, "Sun": False }))

    user = relationship("User", back_populates="streak")
