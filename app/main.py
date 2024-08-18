import os
import requests
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from app.api.auth_router import router as auth_router
from app.api.user_router import router as user_router
from app.api.streak_router import router as streak_router
from app.api.meal_router import router as meal_router
from app.api.recipe_router import router as recipe_router
from app.api.info_router import router as info_router
from app.api.scan_router import router as scan_router
from app.api.recommend_router import router as recommend_router

app = FastAPI()

MODEL_URL = "https://drive.google.com/uc?id=1cVWEMdG7ucHPQrS5vVbZQGep3J9Gm22L&export=download"
MODEL_PATH = "clip_ai_models/clip_finetuned3.pth"

def download_file(url, dest_path):
    """Download a file from a URL to a local path."""
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"Downloaded {dest_path}.")
    else:
        raise Exception(f"Failed to download {url}. Status code: {response.status_code}")

def ensure_model_downloaded():
    """Ensure that the model file is downloaded before starting the app."""
    if not os.path.exists(MODEL_PATH):
        print(f"{MODEL_PATH} not found. Downloading...")
        download_file(MODEL_URL, MODEL_PATH)
    else:
        print(f"{MODEL_PATH} already exists.")

# Run the model download check when the app starts
@app.on_event("startup")
async def startup_event():
    ensure_model_downloaded()

# Custom exception handler for HTTPException
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": [{
                "loc": ["string", 0],  # Example location, adjust as needed
                "msg": exc.detail,  # Detail from the exception
                "type": "authorization"  # Example type, adjust as needed
            }]
        }
    )

# Include routers from different parts of the application
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(streak_router)
app.include_router(meal_router)
app.include_router(recipe_router)
app.include_router(info_router)
app.include_router(scan_router)
app.include_router(recommend_router)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
