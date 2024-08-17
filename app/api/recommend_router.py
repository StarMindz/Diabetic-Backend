from app.utilities.scan import generation_config_recommendation, extract_json
from sqlalchemy.orm import Session
from app.database import get_db
from app.security import get_user
from app.models.user_model import UserProfile, MealPlan, Meal
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
  system_instruction="I need your response in the form of a json that looks like this\n{\n  \"breakfast\": [\n    {\n      \"name\": \"Jellof Rice and Chicken\",\n      \"image\": \"string\",\n      \"recipe\": {\n        \"name\": \"string\",\n        \"glycemic_index\": 90,\n        \"diabetic_friendly\": false,\n        \"instructions\": [\n          \"string\"\n        ],\n        \"carbohydrate_content\": 0,\n        \"protein_content\": 0,\n        \"image\": \"https://example.com/default_image.jpg\",\n        \"calorie_level\": 0,\n        \"recommendations\": \"string\",\n        \"ingredients\": [\n          \"string\"\n        ],\n      }\n    },\n    {\n      \"name\": \"Jellof Rice and Chicken\",\n      \"image\": \"string\",\n      \"recipe\": {\n        \"name\": \"string\",\n        \"glycemic_index\": 90,\n        \"diabetic_friendly\": false,\n        \"instructions\": [\n          \"string\"\n        ],\n        \"carbohydrate_content\": 0,\n        \"protein_content\": 0,\n        \"overall_score\": 0,\n        \"image\": \"https://example.com/default_image.jpg\",\n        \"calorie_level\": 0,\n        \"recommendations\": \"string\",\n        \"ingredients\": [\n          \"string\"\n        ],\n      }\n    }\n  ],\n  \"lunch\": [\n    {\n      \"name\": \"Yam and Egg\",\n      \"image\": \"string\",\n      \"recipe\": {\n        \"name\": \"string\",\n        \"glycemic_index\": 0,\n        \"diabetic_friendly\": true,\n        \"instructions\": [\n          \"string\"\n        ],\n        \"carbohydrate_content\": 0,\n        \"protein_content\": 0,\n        \"overall_score\": 0,\n        \"image\": \"https://example.com/default_image.jpg\",\n        \"calorie_level\": 0,\n        \"recommendations\": \"string\",\n        \"ingredients\": [\n          \"string\"\n        ],\n      }\n    }\n  ],\n  \"dinner\": [\n    {\n      \"name\": \"Eba and Egusi Soup\",\n      \"image\": \"string\",\n      \"recipe\": {\n        \"name\": \"string\",\n        \"glycemic_index\": 0,\n        \"diabetic_friendly\": true,\n        \"instructions\": [\n          \"string\"\n        ],\n        \"carbohydrate_content\": 0,\n        \"protein_content\": 0,\n        \"overall_score\": 0,\n        \"image\": \"https://example.com/default_image.jpg\",\n        \"calorie_level\": 0,\n        \"recommendations\": \"string\",\n        \"ingredients\": [\n          \"string\"\n        ],\n      }\n    }\n  ],\n  \"snack\": [\n    {\n      \"name\": \"Meat pie\",\n      \"image\": \"string\",\n      \"recipe\": {\n        \"name\": \"string\",\n        \"glycemic_index\": 0,\n        \"diabetic_friendly\": true,\n        \"instructions\": [\n          \"string\"\n        ],\n        \"carbohydrate_content\": 0,\n        \"protein_content\": 0,\n        \"overall_score\": 0,\n        \"image\": \"https://example.com/default_image.jpg\",\n        \"calorie_level\": 0,\n        \"recommendations\": \"string\",\n        \"ingredients\": [\n          \"string\"\n        ],\n      }\n    }\n  ]\n}",
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
        f"considering the user profile below.\n\nUser profile:\n{user_profile}\n\n"
        f"Also Consider the Past meal intake data:\n"
    )

    # Add past meals to the prompt
    for day, meals in past_meals.items():
        prompt += f"{day}:\n"
        for meal_type, meal_name in meals.items():
            prompt += f"  {meal_type.capitalize()}: {meal_name}\n"

    prompt += (
        "\nEnsure the meals are accessible in {user.profile.country}, and provide a good balance of macronutrients."
    )
    
    chat_session = model.start_chat(
        history=[
    ]
    )

    response = chat_session.send_message(prompt)

    # Now, convert the cleaned string to a JSON object
    return json.loads(response.text)
