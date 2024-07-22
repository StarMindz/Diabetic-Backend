from pydantic import BaseModel, EmailStr

class UserProfileUpdate(BaseModel):
    height: float
    weight: float
    age: int
    gender: str
    country: str
    allergy: str
    medical_issue: str
    diabetic_type: str
    medication: str

    class Config:
        orm_mode = True

class SignupUser(BaseModel):
    full_name: str
    email: EmailStr
    password: str