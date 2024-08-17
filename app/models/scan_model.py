from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.config import Base
from .mixins import Timestamp
from app.models.meal_model import Meal, MealPlan

class ScanHistory(Timestamp, Base):
    __tablename__ = 'scan_histories'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    scan_result = Column(JSON, nullable=False)

    user = relationship("User", back_populates="scan_history")

