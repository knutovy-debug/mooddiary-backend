from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, entries, subscription

app = FastAPI(title="MoodDiary API")

# Разрешаем запросы с Vercel (и любых других источников, для теста)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Можно поменять на конкретный URL Vercel позже
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
