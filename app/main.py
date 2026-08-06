import os
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.core.database import get_db, engine, Base
from app.models import User, Entry
from app.services.simple_analyzer import analyze_entry
from app.core.dependencies import get_current_user
from app.api.v1 import auth, entries, subscription

app = FastAPI(title="MoodDiary API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    if os.path.exists("mooddiary.db"):
        os.remove("mooddiary.db")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
def root():
    return {"message": "MoodDiary API работает!"}

@app.get("/api/v1/analyze")
async def analyze(
    text: str,
    lang: str = "ru",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # --- Проверка подписки и лимита записей ---
    is_premium = current_user.is_subscribed and current_user.subscription_expires and current_user.subscription_expires > datetime.utcnow()
    
    if not is_premium:
        today = datetime.utcnow().date()
        count = await db.scalar(
            select(func.count(Entry.id)).where(
                Entry.user_id == current_user.id,
                func.date(Entry.created_at) == today
            )
        )
        if count >= 3:
            raise HTTPException(
                status_code=403, 
                detail="Daily limit reached (3 entries). Buy subscription to get unlimited."
            )
    # --- Конец проверки ---

    analysis = analyze_entry(text, lang)
    new_entry = Entry(
        user_id=current_user.id,
        text=text,
        sentiment=analysis["sentiment"],
        stress_level=analysis["stress_level"],
        topics=", ".join(analysis["topics"]),
        recommendation=analysis["recommendation"]
    )
    db.add(new_entry)
    await db.commit()
    await db.refresh(new_entry)
    return analysis

# Подключаем роутеры
app.include_router(auth.router, prefix="/api/v1")
app.include_router(entries.router, prefix="/api/v1")
app.include_router(subscription.router, prefix="/api/v1")