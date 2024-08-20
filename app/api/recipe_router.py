from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.meal_model import Meal, MealPlan, Recipe
from app.schemas.meal_schema import MealCreate, MealOut, MealPlanOut
from app.schemas.meal_schema import RecipeInput
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
        instructions=[instruction for instruction in recipe.instructions],
        carbohydrate_content = recipe.carbohydrate_content,
        protein_content = recipe.protein_content,
        overall_score  = recipe.overall_score,
        fiber_content = recipe.fiber_content,
        net_carb = recipe.net_carb,
        fat = recipe.fat,
        portion_size_recommendations = recipe.portion_size_recommendations,
        cholesterol = recipe.cholesterol
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

@router.post("/like_logic/{recipe_id}")
def like_or_unlike_recipe(recipe_id: int, db: Session = Depends(get_db), user: dict = Depends(get_user)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    likers_id = [item for item in recipe.liked_by] if recipe.liked_by else []

    if user.id in likers_id:
        likers_id.remove(user.id)
        recipe.total_likes -= 1
        message = "Unliked successfully"
    else:
        likers_id.append(user.id)
        recipe.total_likes += 1
        message = "Liked successfully"

    recipe.liked_by = likers_id
    db.commit()
    db.refresh(recipe)
    return {"recipe_id": recipe.id, "total_likes": recipe.total_likes, "message": message, "recipe": recipe}
