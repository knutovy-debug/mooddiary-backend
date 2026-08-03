from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, engine, Base
from app.models import User, Entry
from app.services.simpl_analyzer import analyze_entry
from app.core.dependencies import get_current_user
from app.api.v1 import auth, entries

app = FastAPI(title="MoodDiary API")

# CORS — настройка до подключения роутеров (порядок не важен, но лучше сначала)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # <--- отступ исправлен

@app.get("/")
def root():
    return {"message": "MoodDiary API работает!"}

@app.get("/api/v1/analyze")
async def analyze(
    text: str,
    lang: str = "ru",  # язык по умолчанию — русский
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    analysis = analyze_entry(text, lang)   # передаём язык в анализатор
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