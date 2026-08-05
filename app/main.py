import os
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker, declared_attr
from sqlalchemy import Column, Integer, String, Text, DateTime, select, func
from pydantic import BaseModel
import uvicorn

# ==========================================
# 1. Настройки Базы Данных (SQLite)
# ==========================================
# Используем aiosqlite для асинхронной работы. 
# Если у вас PostgreSQL или MySQL, замените URL.
DATABASE_URL = "sqlite+aiosqlite:///./mooddiary.db"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Базовый класс для моделей
Base = declarative_base()

# ==========================================
# 2. Модели SQLAlchemy (Таблицы БД)
# ==========================================
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Entry(Base):
    __tablename__ = "entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    text = Column(Text)
    sentiment = Column(String)
    stress_level = Column(Integer)
    topics = Column(String)
    recommendation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# ==========================================
# 3. Pydantic Схемы (для типизации ответов)
# ==========================================
class AnalyzeResponse(BaseModel):
    status: str
    message: str
    entry_id: int

# ==========================================
# 4. Создание экземпляра FastAPI
# ==========================================
# ВАЖНО: "app = FastAPI()" ДОЛЖНО БЫТЬ ПЕРЕД ДЕКОРАТОРАМИ @app.get
app = FastAPI(title="MoodDiary API")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # временно разрешаем все источники
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app = FastAPI(title="MoodDiary API")

# ------------------ ДОБАВИТЬ ЭТОТ БЛОК ------------------
origins = [
    "https://mooddiary-frontend-zeta.vercel.app",  # Домен вашего фронтенда
    # "http://localhost:3000",  # Если тестируете локально через React/Vite
    # "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # Разрешаем эти домены
    allow_credentials=True,
    allow_methods=["*"],            # Разрешаем все методы (GET, POST, PUT и т.д.)
    allow_headers=["*"],            # Разрешаем все заголовки
)
# --------------------------------------------------------
# ==========================================
# 5. Зависимости (Dependencies)
# ==========================================
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# Заглушка для получения текущего пользователя.
# В реальном проекте здесь должна быть проверка JWT токена или сессии.
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select

# 1. ВАЖНО: Добавляем auto_error=False
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    # ВРЕМЕННАЯ ЗАГЛУШКА: Игнорируем токен и просто берем любого пользователя из БД
    result = await db.execute(select(User).limit(1))
    user = result.scalar_one_or_none()
    
    # Если пользователей в БД нет - создаем тестового
    if not user:
        user = User(username="test_user", email="test@test.com")
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    return user
def analyze_entry(text):
    """
    Здесь должна быть ваша ИИ-логика или логика обработки текста.
    В данном примере мы симулируем ответ.
    """
    # Пример логики...
    sentiment = "positive" if "хорошо" in text.lower() or "good" in text.lower() else "neutral"
    stress_level = 1 if sentiment == "positive" else 5
    
    return {
        "sentiment": sentiment,
        "stress_level": stress_level,
        "topics": ["общий анализ", "настроение"],
        "recommendation": "Продолжайте отслеживать своё настроение для поддержания баланса."
    }

# ==========================================
# 7. Эндпоинты (API маршруты)
# ==========================================
@app.on_event("startup")
async def startup():
    # Создаем таблицы в БД при запуске сервера
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "MoodDiary API работает!"}

@app.get("/api/v1/analyze", response_model=AnalyzeResponse)
async def analyze(
    text: str,
    lang: str = "ru",              # Аргумент по умолчанию
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. ВЫЗЫВАЕМ функцию и получаем результат
    analysis = analyze_entry(text)

    # 2. Создаем объект записи из полученных данных
    new_entry = Entry(
        user_id=current_user.id,
        text=text,
        sentiment=analysis["sentiment"],
        stress_level=analysis["stress_level"],
        topics=", ".join(analysis["topics"]),
        recommendation=analysis["recommendation"]
    )

    # 3. Сохраняем в базу данных
    db.add(new_entry)
    await db.commit()
    await db.refresh(new_entry)

    # 4. Возвращаем результат клиенту
    return {
        "status": "success",
        "message": "Анализ сохранен",
        "entry_id": new_entry.id
    }

# ==========================================
# 8. Точка входа для запуска
# ==========================================
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    from sqlalchemy import select, desc

# ... (ваш предыдущий код) ...

@app.get("/api/v1/history") # Или просто @app.get("/history") - как вызывается на фронтенде
async def get_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Достаем все записи текущего пользователя из БД, сортируя от новых к старым
    result = await db.execute(
        select(Entry)
        .where(Entry.user_id == current_user.id)
        .order_by(desc(Entry.created_at))
    )
    entries = result.scalars().all()
    
    # Формируем красивый список для фронтенда
    return [
        {
            "id": entry.id,
            "text": entry.text,
            "sentiment": entry.sentiment,
            "stress_level": entry.stress_level,
            "topics": entry.topics,
            "recommendation": entry.recommendation,
            "created_at": entry.created_at.isoformat()
        }
        for entry in entries
    ]