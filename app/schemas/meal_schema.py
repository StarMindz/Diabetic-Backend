from pydantic import BaseModel
from typing import List, Optional, Dict
import datetime

class RecipeOut(BaseModel):
    name: str
    image: str
    glycemic_index: int
    calorie_level: int
    diabetic_friendly: bool
    recommendations: str
    ingredients: List[str]
    instructions: List[str]
    carbohydrate_content: float
    protein_content: float
    overall_score: float
    total_likes: float
    liked_by: List[str] 

class MealOut(BaseModel):
    id: int
    name: str
    meal_type: str
    created_at: datetime.datetime
    recipe: RecipeOut

    class Config:
        orm_mode = True

class MealPlanOut(BaseModel):
    id: int
    date: datetime.date
    meals: List[MealOut]

    class Config:
        orm_mode = True

class Recipe(BaseModel):
    name: str
    image: str
    glycemic_index: int
    calorie_level: int
    diabetic_friendly: bool
    recommendations: str
    ingredients: List[str]
    instructions: List[str]
    carbohydrate_content: float
    protein_content: float
    overall_score: float
    total_likes: float
    liked_by: List[str] 

class MealCreate(BaseModel):
    id: int
    name: Optional[str]
    image: Optional[str]
    recipe: Optional[Recipe]

class DailyMeals(BaseModel):
    breakfast: List[MealCreate]
    lunch: List[MealCreate]
    dinner: List[MealCreate]
    snack: List[MealCreate]
