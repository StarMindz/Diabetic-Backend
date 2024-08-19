from pydantic import BaseModel, EmailStr
from typing import Any

class UserProfileUpdate(BaseModel):
    height: float
    weight: float
    age: int
    gender: str
    country: str
    alergy: str
    medical_issue: str
    diabetic_type: str
    medication: str

class SignupUser(BaseModel):
    full_name: str
    email: EmailStr
    password: str

class UserProfileResponse(BaseModel):
    image: Any
    height: Any
    weight: Any
    age: Any
    gender: Any
    country: Any
    alergy: Any
    medical_issue: Any
    diabetic_type: Any
    medication: Any

    class Config:
        orm_mode = True