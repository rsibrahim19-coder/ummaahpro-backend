from pydantic import BaseModel
from typing import List, Optional

AMAL_DEEDS = [
    {"id": "quran_read", "name": "Read Quran", "category": "Quran", "emoji": "📖"},
    {"id": "dhikr_morning", "name": "Morning Dhikr", "category": "Dhikr", "emoji": "🌅"},
    {"id": "dhikr_evening", "name": "Evening Dhikr", "category": "Dhikr", "emoji": "🌇"},
    {"id": "istigfar", "name": "Istighfar (100x)", "category": "Dhikr", "emoji": "🤲"},
    {"id": "tahajjud", "name": "Tahajjud Prayer", "category": "Prayer", "emoji": "🌙"},
    {"id": "fasting", "name": "Voluntary Fast", "category": "Fasting", "emoji": "🌙"},
    {"id": "sadaqah", "name": "Give Sadaqah", "category": "Charity", "emoji": "❤️"},
    {"id": "helping", "name": "Help Someone", "category": "Character", "emoji": "🤝"},
]

class AmalEntry(BaseModel):
    date: str
    deeds: List[str]
    notes: Optional[str] = None

class AmalResponse(BaseModel):
    date: str
    deeds: List[str]
    completed_count: int
    streak: int

class AmalStatsResponse(BaseModel):
    total_deeds_this_week: int
    most_frequent_deed: Optional[str]
    streak: int
    best_day: Optional[str]
