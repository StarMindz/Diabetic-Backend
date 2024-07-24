from sqlalchemy import Column, Integer, Date, ForeignKey
from datetime import date
from sqlalchemy.orm import relationship
from app.config import Base

class Streak(Base):
    __tablename__ = "streaks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity = Column(Date, default=date.today())

    user = relationship("User", back_populates="streak")
