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
    prefix="/meals",
    tags=["Meals"]
)

def get_or_create_meal_plan(db: Session, user_id: int, date: datetime.date):
    meal_plan = db.query(MealPlan).filter(MealPlan.user_id == user_id, MealPlan.date == date).first()
    if not meal_plan:
        meal_plan = MealPlan(user_id=user_id, date=date)
        db.add(meal_plan)
        db.commit()
        db.refresh(meal_plan)
    return meal_plan

def delete_meal_plan_if_empty(db: Session, meal_plan_id: int):
    meal_plan = db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()
    if meal_plan and len(meal_plan.meals) == 0:
        db.delete(meal_plan)
        db.commit()

@router.post("/breakfast")
def add_breakfast(meal: MealCreate, date: datetime.date, db: Session = Depends(get_db), user:dict = Depends(get_user)):
    meal_plan = get_or_create_meal_plan(db, user.id, date)
    new_meal = Meal(name=meal.name, image=meal.image, meal_type="breakfast", meal_plan_id=meal_plan.id)
    if meal.recipe:
        new_meal.recipe = Recipe(**meal.recipe.dict())
    db.add(new_meal)
    db.commit()
    db.refresh(new_meal)
    return {"message": "Meal Created Successfully", "Meal": new_meal}

@router.post("/lunch")
def add_lunch(meal: MealCreate, date: datetime.date, db: Session = Depends(get_db), user:dict = Depends(get_user)):
    meal_plan = get_or_create_meal_plan(db, user.id, date)
    new_meal = Meal(name=meal.name, image=meal.image, meal_type="lunch", meal_plan_id=meal_plan.id)
    if meal.recipe:
        new_meal.recipe = Recipe(**meal.recipe.dict())
    db.add(new_meal)
    db.commit()
    db.refresh(new_meal)
    return {"message": "Meal Created Successfully", "Meal": new_meal}

@router.post("/dinner")
def add_dinner(meal: MealCreate, date: datetime.date, db: Session = Depends(get_db), user:dict = Depends(get_user)):
    meal_plan = get_or_create_meal_plan(db, user.id, date)
    new_meal = Meal(name=meal.name, image=meal.image, meal_type="dinner", meal_plan_id=meal_plan.id)
    if meal.recipe:
        new_meal.recipe = Recipe(**meal.recipe.dict())
    db.add(new_meal)
    db.commit()
    db.refresh(new_meal)
    return {"message": "Meal Created Successfully", "Meal": new_meal}

@router.post("/snack")
def add_snack(meal: MealCreate, date: datetime.date, db: Session = Depends(get_db), user:dict = Depends(get_user)):
    meal_plan = get_or_create_meal_plan(db, user.id, date)
    new_meal = Meal(name=meal.name, image=meal.image, meal_type="snack", meal_plan_id=meal_plan.id)
    if meal.recipe:
        new_meal.recipe = Recipe(**meal.recipe.dict())
    db.add(new_meal)
    db.commit()
    db.refresh(new_meal)
    return {"message": "Meal Created Successfully", "Meal": new_meal}

@router.delete("/breakfast/{meal_id}", response_model=MealOut)
def delete_breakfast(meal_id: int, date: datetime.date, db: Session = Depends(get_db), user:dict = Depends(get_user)):
    meal = db.query(Meal).filter(Meal.id == meal_id, Meal.meal_type == "breakfast", Meal.meal_plan.has(user_id=user.id, date=date)).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    meal_plan_id = meal.meal_plan_id
    db.delete(meal)
    db.commit()
    delete_meal_plan_if_empty(db, meal_plan_id)
    return {"message": "Meal Deleted Successfully", "Meal": meal}

@router.delete("/lunch/{meal_id}", response_model=MealOut)
def delete_lunch(meal_id: int, date: datetime.date, db: Session = Depends(get_db), user:dict = Depends(get_user)):
    meal = db.query(Meal).filter(Meal.id == meal_id, Meal.meal_type == "lunch", Meal.meal_plan.has(user_id=user.id, date=date)).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    meal_plan_id = meal.meal_plan_id
    db.delete(meal)
    db.commit()
    delete_meal_plan_if_empty(db, meal_plan_id)
    return {"message": "Meal Deleted Successfully", "Meal": meal}

@router.delete("/dinner/{meal_id}", response_model=MealOut)
def delete_dinner(meal_id: int, date: datetime.date, db: Session = Depends(get_db), user:dict = Depends(get_user)):
    meal = db.query(Meal).filter(Meal.id == meal_id, Meal.meal_type == "dinner", Meal.meal_plan.has(user_id=user.id, date=date)).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    meal_plan_id = meal.meal_plan_id
    db.delete(meal)
    db.commit()
    delete_meal_plan_if_empty(db, meal_plan_id)
    return {"message": "Meal Deleted Successfully", "Meal": meal}

@router.delete("/snack/{meal_id}", response_model=MealOut)
def delete_snack(meal_id: int, date: datetime.date, db: Session = Depends(get_db), user:dict = Depends(get_user)):
    meal = db.query(Meal).filter(Meal.id == meal_id, Meal.meal_type == "snack", Meal.meal_plan.has(user_id=user.id, date=date)).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    meal_plan_id = meal.meal_plan_id
    db.delete(meal)
    db.commit()
    delete_meal_plan_if_empty(db, meal_plan_id)
    return {"message": "Meal Deleted Successfully", "Meal": meal}

@router.get("/{date}", response_model=MealPlanOut)
def get_meal_plan(date: datetime.date, db: Session = Depends(get_db), user:dict = Depends(get_user)):
    meal_plan = db.query(MealPlan).filter(MealPlan.user_id == user.id, MealPlan.date == date).first()
    if not meal_plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return meal_plan

