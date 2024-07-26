from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.config import Base
from .mixins import Timestamp
from app.models.meal_model import Meal, MealPlan

class User(Timestamp, Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    streak = relationship("Streak", back_populates="user", uselist=False)
    meal_plans = relationship("MealPlan", back_populates="user")
    scan_history = relationship("ScanHistory", back_populates="user")

    def create_meal_plan(self, date):
        meal_plan = MealPlan(user_id=self.id, date=date)
        return meal_plan

class UserProfile(Timestamp, Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    country = Column(String, nullable=True)
    alergy = Column(String, nullable=True)
    medical_issue = Column(String, nullable=True)
    diabetic_type = Column(String, nullable=True)  
    medication = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship("User", back_populates="profile")
