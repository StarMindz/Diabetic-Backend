import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
from app.database import get_db
from app.security import get_user
import os

router = APIRouter(tags=["News"])

load_dotenv()

NEWS_KEY = os.environ.get("NEWS_API")

# Get today's date
today = datetime.today()

# Calculate the date 20 days from today
future_date = today + timedelta(days=20)

# Format the date in "YYYY-MM-DD" format
formatted_date = future_date.strftime("%Y-%d-%m")

@router.post("/get_news")
async def get_news(db: Session = Depends(get_db), user: dict = Depends(get_user)):
    print(formatted_date)
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "diabetes",
        "from": formatted_date,
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
