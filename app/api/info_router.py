from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.meal_model import Meal, MealPlan, Recipe
from app.schemas.meal_schema import MealCreate, MealOut, MealPlanOut
from app.schemas.meal_schema import Recipe as RecipeInput
from app.models.user_model import User
from app.security import get_user
from app.database import get_db
import datetime

router = APIRouter(
    prefix="/daily-info",
    tags=["Meal Information"]
)

@router.get("/total_calories/{date}", response_model=dict)
def get_total_calories(date: datetime.date, db: Session = Depends(get_db), user: dict = Depends(get_user)):
    meal_plan = db.query(MealPlan).filter(MealPlan.user_id == user.id, MealPlan.date == date).first()
    if not meal_plan:
        raise HTTPException(status_code=404, detail="Meal plan not found for the specified date")

    total_calories = sum(meal.recipe.calorie_level for meal in meal_plan.meals if meal.recipe)
    return {"date": date, "total_calories": total_calories}

@router.get("/total_glycemic_load/{date}", response_model=dict)
def get_total_glycemic_load(date: datetime.date, db: Session = Depends(get_db), user: dict = Depends(get_user)):
    meal_plan = db.query(MealPlan).filter(MealPlan.user_id == user.id, MealPlan.date == date).first()
    if not meal_plan:
        raise HTTPException(status_code=404, detail="Meal plan not found for the specified date")

    total_glycemic_load = sum((meal.recipe.glycemic_index * meal.recipe.carbohydrate_content / 100) for meal in meal_plan.meals if meal.recipe)
    return {"date": date, "total_glycemic_load": total_glycemic_load}




