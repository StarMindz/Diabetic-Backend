import os
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

app = FastAPI()

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
