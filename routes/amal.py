from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from collections import Counter

from database import amal_collection
from models.amal import AmalEntry, AmalResponse, AmalStatsResponse, AMAL_DEEDS
from routes.auth import get_current_user

router = APIRouter(prefix="/amal", tags=["amal"])


async def _amal_streak(user_id: str) -> int:
    streak = 0
    check_date = datetime.utcnow().date()
    for _ in range(365):
        date_str = check_date.isoformat()
        entry = await amal_collection.find_one({"user_id": user_id, "date": date_str})
        if entry and entry.get("deeds"):
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    return streak


@router.get("/deeds")
async def list_deeds():
    grouped = {}
    for deed in AMAL_DEEDS:
        cat = deed["category"]
        grouped.setdefault(cat, []).append(deed)
    return {"categories": grouped, "all": AMAL_DEEDS}


@router.post("/log", response_model=AmalResponse)
async def log_amal(entry: AmalEntry, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    await amal_collection.update_one(
        {"user_id": user_id, "date": entry.date},
        {"$set": {"deeds": entry.deeds, "notes": entry.notes, "updated_at": datetime.utcnow()}},
        upsert=True
    )
    streak = await _amal_streak(user_id)
    return AmalResponse(date=entry.date, deeds=entry.deeds, completed_count=len(entry.deeds), streak=streak)


@router.get("/today", response_model=AmalResponse)
async def get_today_amal(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    today = datetime.utcnow().date().isoformat()
    entry = await amal_collection.find_one({"user_id": user_id, "date": today})
    deeds = entry["deeds"] if entry else []
    streak = await _amal_streak(user_id)
    return AmalResponse(date=today, deeds=deeds, completed_count=len(deeds), streak=streak)


@router.get("/stats", response_model=AmalStatsResponse)
async def get_amal_stats(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    today = datetime.utcnow().date()
    week_start = today - timedelta(days=6)
    all_deeds = []
    best_day = None
    best_count = 0
    for i in range(7):
        d = (week_start + timedelta(days=i)).isoformat()
        entry = await amal_collection.find_one({"user_id": user_id, "date": d})
        if entry and entry.get("deeds"):
            all_deeds.extend(entry["deeds"])
            if len(entry["deeds"]) > best_count:
                best_count = len(entry["deeds"])
                best_day = d
    most_frequent = Counter(all_deeds).most_common(1)
    streak = await _amal_streak(user_id)
    return AmalStatsResponse(
        total_deeds_this_week=len(all_deeds),
        most_frequent_deed=most_frequent[0][0] if most_frequent else None,
        streak=streak,
        best_day=best_day
    )
