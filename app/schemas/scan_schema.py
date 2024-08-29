from pydantic import BaseModel
from typing import Dict
import datetime

class ScanHistorySchema(BaseModel):
    id: int
    created_at: datetime.datetime
    scan_result: Dict

    class Config:
        from_attributes = True
