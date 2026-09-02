from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api.v1 import auth, entries, subscription

# ВАЖНО: Создаем все таблицы при запуске сервера!
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MoodDiary API")

# Разрешаем запросы с Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(entries.router, prefix="/api/v1")
app.include_router(subscription.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "MoodDiary API"}
