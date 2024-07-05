from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()

@app.get("/{item_id}")
async def test(item_id: str, query: str = "100"):
    return {"hello": "world", item_id: query}