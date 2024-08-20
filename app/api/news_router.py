import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import requests
from dotenv import load_dotenv
from app.database import get_db
from app.security import get_user
import os

router = APIRouter(tags=["News"])

load_dotenv()

NEWS_KEY = os.environ.get("NEWS_API")

@router.post("/get_news")
async def get_news(db: Session = Depends(get_db), user: dict = Depends(get_user)):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "diabetes",
        "from": "2024-07-20",
        "sortBy": "popularity",
        "apiKey": NEWS_KEY,
        "language":"en"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors

        articles = response.json().get("articles", [])
        
        # Select 5 random articles
        selected_articles = random.sample(articles, min(len(articles), 5))
        
        # Format the selected articles
        formatted_articles = [
            {
                "id": idx + 1,
                "title": article.get("title", ""),
                "subTitle": article.get("author", ""),
                "imageUrl": article.get("urlToImage", ""),
                "thumbnailUrl": article.get("urlToImage", ""),  # Assuming you want to use a default icon
                "source": article.get("source", {}).get("name", ""),
                "date": article.get("publishedAt", "").split("T")[0],  # Date in 'YYYY-MM-DD' format
                "content": article.get("content", ""),
            }
            for idx, article in enumerate(selected_articles)
        ]

        return formatted_articles

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
