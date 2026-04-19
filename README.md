# UmmahPro Backend API

FastAPI + MongoDB backend for the UmmahPro iOS app.

## Setup

1. Copy `.env.example` to `.env` and fill in your credentials
2. Run `pip install -r requirements.txt`
3. Run `python main.py`

## Deploy to Render.com

1. Push to GitHub
2. Go to render.com → New Web Service
3. Connect your GitHub repo
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add env vars from your `.env`
