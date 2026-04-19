from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

client = AsyncIOMotorClient(MONGODB_URL)
db = client.ummaahpro

users_collection = db.users
prayer_logs_collection = db.prayer_logs
amal_collection = db.amal_entries
chat_collection = db.chat_sessions
