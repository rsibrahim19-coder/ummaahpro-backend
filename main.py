from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

from routes.auth import router as auth_router
from routes.prayers import router as prayers_router
from routes.amal import router as amal_router
from routes.ai_chat import router as ai_router

app = FastAPI(
    title="UmmahPro API",
    description="Backend for UmmahPro",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(prayers_router)
app.include_router(amal_router)
app.include_router(ai_router)

@app.get("/")
async def health():
    return {"status": "online", "app": "UmmahPro API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
