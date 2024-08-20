from app.utilities.scan import generation_config_recommendation, extract_json
from sqlalchemy.orm import Session
from app.database import get_db
from app.security import get_user
from app.models.user_model import UserProfile, MealPlan, Meal
from app.models.meal_model import Recipe
from fastapi import APIRouter, Depends, HTTPException
from dotenv import load_dotenv
import google.generativeai as genai
import os
import json

router = APIRouter(tags=["Recommendation"])

load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Configure the Gemini Vision Pro model with detailed instructions
model = genai.GenerativeModel(
  model_name="gemini-1.5-pro",
  generation_config=generation_config_recommendation,
  system_instruction="I need your response in the form of a json that looks like this, where meal_id is the is the index of the recommended meal in my list of possible meals. Do not use meal names directly\n{\n  \"breakfast\": [\n      meal_id\n  ],\n  \"lunch\": [\n      meal_id\n  ],\n  \"dinner\": [\n      meal_id\n  ],\n  \"snack\": [\n      meal_id\n  ]\n}\n\n",
)

def clean_json_string(text_response):
    # This removes escape characters and formats the string as a valid JSON structure
    text_response = text_response.replace('\n', '').replace('\\', '').replace('\"', '"')
    return text_response

@router.get("/recommend")
async def get_recommendations(db: Session = Depends(get_db), user: dict = Depends(get_user)):
    # Retrieve user profile
    if not user.profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    # Retrieve past two days of meal plans
    past_meal_plans = db.query(MealPlan).filter(MealPlan.user_id == user.id).order_by(MealPlan.date.desc()).limit(2).all()
    
    if not past_meal_plans:
        raise HTTPException(status_code=404, detail="No past meal plans found")

    # Format user profile information
    user_profile = (
        f"Name: {user.full_name}\n"
        f"Height: {user.profile.height}cm\n"
        f"Weight: {user.profile.weight}kg\n"
        f"Allergies: {user.profile.alergy or 'None'}\n"
        f"Gender: {user.profile.gender}\n"
        f"Age: {user.profile.age}\n"
        f"Country: {user.profile.country}\n"
        f"Medical Issues: {user.profile.medical_issue or 'None'}\n"
        f"Medications: {user.profile.medication or 'None'}"
    )

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

    valid_recipes_names = [recipe.name for recipe in valid_recipes]

    # Collect past meals data
    past_meals = {}
    for idx, meal_plan in enumerate(past_meal_plans):
        day_key = f"Day {idx + 1}"
        past_meals[day_key] = {
            "breakfast": ", ".join([meal.name for meal in meal_plan.meals if meal.meal_type == 'breakfast']) or "None",
            "lunch": ", ".join([meal.name for meal in meal_plan.meals if meal.meal_type == 'lunch']) or "None",
            "dinner": ", ".join([meal.name for meal in meal_plan.meals if meal.meal_type == 'dinner']) or "None",
            "snacks": ", ".join([meal.name for meal in meal_plan.meals if meal.meal_type == 'snack']) or "None",
        }

    # Build the prompt based on user profile and past meal plans
    prompt = (
        f"Given the following user profile and past meal intake data, please recommend a balanced and nutritious one day meal plan containing "
        f"breakfast, lunch, dinner, and snacks. The recommendations should be suitable for managing {user.profile.diabetic_type} Diabetes, "
        f"Make sure to consider the user profile below.\n\nUser profile:\n{user_profile}\n\n"
        f"Make sure to consider the Past meal intake data in your decision making:"
    )

    # Add past meals to the prompt
    for day, meals in past_meals.items():
        prompt += f"{day}:\n"
        for meal_type, meal_name in meals.items():
            prompt += f"  {meal_type.capitalize()}: {meal_name}\n"

    prompt += (
        f"\nThe goal is to maintain optimal blood sugar levels and low Glycemic Load over time and prevent spikes. Don't repeat meals in same day. Provide a good balance of macronutrients and diversity. \n. ONLY PICK MEALS FROM THIS LIST OF POSSIBLE MEALS: {valid_recipes_names}."
    )
    
    chat_session = model.start_chat(
        history=[
    ]
    )

    response = chat_session.send_message(prompt)

    # Now, convert the cleaned string to a JSON object
    result = json.loads(response.text)
    result["breakfast"][0] = {
        "id": 1,
        "name": valid_recipes_names[int(result["breakfast"][0])],
        "image": valid_recipes[int(result["breakfast"][0])].image,
        "recipe": valid_recipes[int(result["breakfast"][0])]
    }

    result["lunch"][0] = {
        "id": 2,
        "name": valid_recipes_names[int(result["lunch"][0])],
        "image": valid_recipes[int(result["lunch"][0])].image,
        "recipe": valid_recipes[int(result["lunch"][0])]
    }

    result["dinner"][0] = {
        "id": 3,
        "name": valid_recipes_names[int(result["dinner"][0])],
        "image": valid_recipes[int(result["dinner"][0])].image,
        "recipe": valid_recipes[int(result["dinner"][0])]
    }

    result["snack"][0] = {
        "id": 4,
        "name": valid_recipes_names[int(result["snack"][0])],
        "image": valid_recipes[int(result["snack"][0])].image,
        "recipe": valid_recipes[int(result["snack"][0])]
    }
    
    return result
