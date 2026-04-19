from fastapi import APIRouter, Depends
from datetime import datetime, timedelta

from database import prayer_logs_collection
from models.prayer_log import PrayerLogEntry, PrayerLogResponse, WeeklySummary
from routes.auth import get_current_user

router = APIRouter(prefix="/prayers", tags=["prayers"])

async def _calculate_streak(user_id: str) -> int:
    streak = 0
    check_date = datetime.utcnow().date()
    for _ in range(365):
        date_str = check_date.isoformat()
        log = await prayer_logs_collection.find_one({"user_id": user_id, "date": date_str})
        if log and log.get("prayers_completed"):
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    return streak

@router.post("/log", response_model=PrayerLogResponse)
async def log_prayers(entry: PrayerLogEntry, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    await prayer_logs_collection.update_one({"user_id": user_id, "date": entry.date}, {"$set": {"prayers_completed": entry.prayers_completed, "updated_at": datetime.utcnow()}}, upsert=True)
    streak = await _calculate_streak(user_id)
    return PrayerLogResponse(date=entry.date, prayers_completed=entry.prayers_completed, completed_count=len(entry.prayers_completed), streak=streak)

@router.get("/today", response_model=PrayerLogResponse)
async def get_today(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    today = datetime.utcnow().date().isoformat()
    log = await prayer_logs_collection.find_one({"user_id": user_id, "date": today})
    prayers = log["prayers_completed"] if log else []
    streak = await _calculate_streak(user_id)
    return PrayerLogResponse(date=today, prayers_completed=prayers, completed_count=len(prayers), streak=streak)

@router.get("/streak")
async def get_streak(current_user: dict = Depends(get_current_user)):
    return {"streak": await _calculate_streak(str(current_user["_id"]))}

@router.get("/weekly", response_model=WeeklySummary)
async def get_weekly_summary(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    today = datetime.utcnow().date()
    week_start = today - timedelta(days=6)
    days = []
    best_day = None
    best_count = 0
    for i in range(7):
        d = (week_start + timedelta(days=i)).isoformat()
        log = await prayer_logs_collection.find_one({"user_id": user_id, "date": d})
        prayers = log["prayers_completed"] if log else []
        count = len(prayers)
        days.append(PrayerLogResponse(date=d, prayers_completed=prayers, completed_count=count, streak=0))
        if count > best_count:
            best_count = count
            best_day = d
    return WeeklySummary(week_start=week_start.isoformat(), days=days, best_day=best_day, average_prayers_per_day=round(sum(d.completed_count for d in days)/7, 1))
