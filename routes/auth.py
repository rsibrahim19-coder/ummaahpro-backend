from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from bson import ObjectId
import os

from database import users_collection
from models.user import UserCreate, UserLogin, UserResponse, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_DAYS = 30

def create_token(user_id: str) -> str:
    payload = {"sub": user_id, "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRY_DAYS)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.post("/register", response_model=TokenResponse)
async def register(data: UserCreate):
    existing = await users_collection.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = pwd_context.hash(data.password)
    now = datetime.utcnow()
    user_doc = {"email": data.email, "password_hash": hashed, "name": data.name, "level": data.level, "created_at": now}
    result = await users_collection.insert_one(user_doc)
    user_id = str(result.inserted_id)
    token = create_token(user_id)
    return TokenResponse(access_token=token, user=UserResponse(id=user_id, email=data.email, name=data.name, level=data.level, created_at=now.isoformat()))

@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    user = await users_collection.find_one({"email": data.email})
    if not user or not pwd_context.verify(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    user_id = str(user["_id"])
    token = create_token(user_id)
    return TokenResponse(access_token=token, user=UserResponse(id=user_id, email=user["email"], name=user["name"], level=user.get("level", "New Muslim"), created_at=user["created_at"].isoformat()))

@router.get("/me", response_model=UserResponse)
async def me(current_user: dict = Depends(get_current_user)):
    return UserResponse(id=str(current_user["_id"]), email=current_user["email"], name=current_user["name"], level=current_user.get("level", "New Muslim"), created_at=current_user["created_at"].isoformat())
