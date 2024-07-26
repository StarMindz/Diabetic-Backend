from pydantic import BaseModel
from typing import List, Optional
import datetime

class MealCreate(BaseModel):
    name: str
    recipe_id: Optional[int] = None

class MealOut(BaseModel):
    id: int
    name: str
    meal_type: str
    created_at: datetime.datetime

    class Config:
        orm_mode = True

class MealPlanOut(BaseModel):
    id: int
    date: datetime.date
    meals: List[MealOut]

    class Config:
        orm_mode = True
