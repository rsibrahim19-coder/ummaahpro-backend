from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import httpx, os, random

from database import amal_collection, prayer_logs_collection
from routes.auth import get_current_user

router = APIRouter(prefix="/ai", tags=["ai"])
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

SYSTEM_PROMPT = """You are a knowledgeable, compassionate Islamic scholar assistant named Malik.
You help Muslims understand Islam with patience, wisdom, and kindness.
Keep responses concise and warm. Use Islamic greetings when appropriate."""

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    user_level: Optional[str] = "New Muslim"

class ChatResponse(BaseModel):
    reply: str

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in request.messages:
        messages.append({"role": m.role, "content": m.content})
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post("https://api.openai.com/v1/chat/completions", headers={"Authorization": f"Bearer {OPENAI_API_KEY}"}, json={"model": "gpt-4o-mini", "messages": messages, "max_tokens": 500})
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail="AI service error")
        reply = resp.json()["choices"][0]["message"]["content"]
    return ChatResponse(reply=reply.strip())

@router.get("/daily-question")
async def daily_question(current_user: dict = Depends(get_current_user)):
    user_name = current_user.get("name", "").split()[0] or "friend"
    questions = [
        {"question": f"As-salamu alaykum {user_name}! How was your Fajr this morning?", "type": "prayer_check"},
        {"question": f"Have you done your morning dhikr today, {user_name}?", "type": "amal_reminder"},
        {"question": f"Is there anything about Islam you've been curious about lately, {user_name}?", "type": "learning"},
    ]
    return random.choice(questions)
