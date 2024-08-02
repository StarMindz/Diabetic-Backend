from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Date, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from app.config import Base
from .mixins import Timestamp
from datetime import datetime

# Mealplan model
class MealPlan(Timestamp, Base):
    __tablename__ = 'meal_plans'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(Date, default=datetime.today)
    meals = relationship("Meal", back_populates="meal_plan")

    user = relationship("User", back_populates="meal_plans")

    # def add_meal_to_plan(self, recipe, meal_type):
    #     meal = Meal(meal_plan_id=self.id, recipe_id=recipe.id, meal_type=meal_type)
    #     return meal


# Meal model 
class Meal(Timestamp,Base):
    __tablename__ = 'meals'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    image = Column(String, nullable=False)
    meal_plan_id = Column(Integer, ForeignKey('meal_plans.id'), nullable=False)
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=True)
    meal_type = Column(String, nullable=False)  # e.g., breakfast, lunch, dinner, snack

    meal_plan = relationship("MealPlan", back_populates="meals")
    recipe = relationship("Recipe")
    scan_histories = relationship("ScanHistory", back_populates="meal")

    def change_recipe(self, new_recipe):
        self.recipe_id = new_recipe.id

# Recipe model
class Recipe(Timestamp, Base):
    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False, default="string")
    image = Column(String, nullable=True)
    glycemic_index = Column(Integer, nullable=False)
    calorie_level = Column(Integer, nullable=False)
    diabetic_friendly = Column(Boolean, nullable=False)
    recommendations = Column(Text, nullable=True)
    instructions = Column(JSON, nullable=False) 
    ingredients = Column(JSON, nullable=False)
    carbohydrate_content = Column(Float, nullable=False, default=0.0) 
    protein_content = Column(Float, nullable=False, default=0.0)
    overall_score  = Column(Float, nullable=False, default=0.0)
    total_likes = Column(Integer, nullable=False, default=0.0)
    liked_by = Column(JSON, nullable=False, default=list)
    
    meals = relationship("Meal", back_populates="recipe")

    def update_recommendations(self, recommendations):
        self.recommendations = recommendations
