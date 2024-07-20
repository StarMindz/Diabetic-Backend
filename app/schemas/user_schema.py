from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserProfileBase(BaseModel):
    full_name: str
    height: float
    weight: float
    age: int
    gender: str
    country: str
    alergy: Optional[str] = None
    medical_issue: Optional[str] = None
    diabetic_type: str
    medication: Optional[str] = None

class UserProfileCreate(UserProfileBase):
    pass

class UserProfile(UserProfileBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    profile: Optional[UserProfile] = None

    class Config:
        orm_mode = True

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

