from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.config import Base
from .mixins import Timestamp

class User(Timestamp, Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    profile = relationship("UserProfile", back_populates="owner", uselist=False)

class UserProfile(Timestamp, Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    height = Column(Float)
    weight = Column(Float)
    age = Column(Integer)
    gender = Column(String)
    country = Column(String)
    alergy = Column(String)
    medical_issue = Column(String)
    diabetic_type = Column(String)  
    medication = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    owner = relationship("User", back_populates="profile")
