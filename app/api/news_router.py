from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import EmailStr
import requests
from app.database import get_db
from app.utilities.streak import update_streak
from app.security import  get_user
import os

router = APIRouter(tags=["News"])

NEWS_KEY = os.environ.get("NEWSKEY")

@router.post("/get_news")
async def get_news(db: Session = Depends(get_db), user:dict = Depends(get_user)):
    url = f"https://newsapi.org/v2/everything"
    params = {
        "q": "diabetes",
        "from": "2024-07-20",
        "sortBy": "popularity",
        "apiKey": NEWS_KEY,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()  # Return JSON response
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
