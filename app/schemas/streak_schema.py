from pydantic import BaseModel
from datetime import date
from typing import Any

class StreakResponse(BaseModel):
    # List all the fields you want to include in the response
    current_streak: int
    longest_streak: int
    last_activity: date
    week: Any  # Or use `dict` if the structure is known

    class Config:
        orm_mode = True
