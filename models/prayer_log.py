from pydantic import BaseModel
from typing import List, Optional

class PrayerLogEntry(BaseModel):
    date: str
    prayers_completed: List[str]

class PrayerLogResponse(BaseModel):
    date: str
    prayers_completed: List[str]
    completed_count: int
    streak: int

class WeeklySummary(BaseModel):
    week_start: str
    days: List[PrayerLogResponse]
    best_day: Optional[str]
    average_prayers_per_day: float
