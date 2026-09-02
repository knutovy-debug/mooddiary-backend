from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, sync_engine
from app.api.v1 import auth, entries, subscription

# ВАЖНО: Создаем таблицы через sync_engine
Base.metadata.create_all(bind=sync_engine)

app = FastAPI(title="MoodDiary API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False, # Меняем на False, чтобы работало с "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(entries.router, prefix="/api/v1")
app.include_router(subscription.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "MoodDiary API"}
