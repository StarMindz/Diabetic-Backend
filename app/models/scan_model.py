from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.config import Base
from .mixins import Timestamp
from app.models.meal_model import Meal, MealPlan

class ScanHistory(Timestamp, Base):
    __tablename__ = 'scan_histories'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    meal_id = Column(Integer, ForeignKey('meals.id'))

    user = relationship("User", back_populates="scan_history")
    meal = relationship("Meal", back_populates="scan_histories")
