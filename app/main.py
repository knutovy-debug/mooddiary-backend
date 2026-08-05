import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, engine, Base
from app.models import User, Entry
from app.services.ai.fallback import analyze_entry
from app.core.dependencies import get_current_user
from app.api.v1 import auth, entries

app = FastAPI(title="MoodDiary API")

# CORS — разрешаем все источники для теста
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# При старте удаляем старую базу и создаём заново с правильной схемой
@app.on_event("startup")
async def startup():
    # Удаляем существующий файл БД, если он есть
    if os.path.exists("mooddiary.db"):
        os.remove("mooddiary.db")
        print("Старая база данных удалена.")
    # Создаём таблицы заново
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Таблицы созданы.")

@app.get("/")
def root():
    return {"message": "MoodDiary API работает!"}

@app.get("/api/v1/analyze")
async def analyze(
    text: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    analysis = analyze_entry(text)
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

# Подключаем роутеры (регистрация, логин, история, статистика)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(entries.router, prefix="/api/v1")