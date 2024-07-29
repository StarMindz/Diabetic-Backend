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
    prefix="/recipe",
    tags=["Recipes"]
)

@router.post("/add_recipe")
def create_recipe(recipe: RecipeInput, db: Session = Depends(get_db)):
    db_recipe = Recipe(
        name=recipe.name,
        image=recipe.image,
        glycemic_index=recipe.glycemic_index,
        calorie_level=recipe.calorie_level,
        diabetic_friendly=recipe.diabetic_friendly,
        recommendations=recipe.recommendations,
        ingredients=[ingredient for ingredient in recipe.ingredients],
        instructions=[instruction for instruction in recipe.instructions]
    )
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return {"message": "Recipe added successfully", "recipe": db_recipe}

@router.get("/get_recipes")
def get_valid_recipes(db: Session = Depends(get_db), user:dict = Depends(get_user)):
    valid_recipes = db.query(Recipe).filter(
        Recipe.name != None,
        Recipe.name != "string",
        Recipe.image != "string",
        Recipe.image != None,
        Recipe.glycemic_index >= 0,
        Recipe.calorie_level >= 0,
        Recipe.diabetic_friendly!=None,
        Recipe.recommendations!= "string",
        Recipe.recommendations!= None,
        Recipe.ingredients != None,
        Recipe.instructions != None
    ).all()
    return valid_recipes
