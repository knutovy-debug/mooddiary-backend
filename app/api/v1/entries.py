from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from datetime import datetime
from app.core.database import get_db
from app.models.entry import Entry
from app.models.user import User
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/entries", tags=["entries"])

@router.get("/my")
async def get_my_entries(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Entry)
        .where(Entry.user_id == current_user.id)
        .order_by(desc(Entry.created_at))
    )
    entries = result.scalars().all()
    return entries

@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from collections import Counter
    result = await db.execute(
        select(Entry)
        .where(Entry.user_id == current_user.id)
        .order_by(Entry.created_at)
    )
    entries = result.scalars().all()
    if not entries:
        return {"dates": [], "sentiments": [], "stress": [], "topics": {}}
    dates = [e.created_at.strftime("%Y-%m-%d") for e in entries]
    sentiment_map = {"positive": 1, "neutral": 0, "negative": -1}
    sentiments = [sentiment_map.get(e.sentiment, 0) for e in entries]
    stress = [e.stress_level for e in entries]
    topics = []
    for e in entries:
        if e.topics:
            topics.extend(e.topics.split(", "))
    topic_counts = Counter(topics)
    return {
        "dates": dates,
        "sentiments": sentiments,
        "stress": stress,
        "topics": dict(topic_counts)
    }

# --- НОВЫЙ ЭНДПОИНТ ДЛЯ СЧЁТЧИКА ЗАПИСЕЙ ---
@router.get("/today-count")
async def get_today_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = datetime.utcnow().date()
    count = await db.scalar(
        select(func.count(Entry.id)).where(
            Entry.user_id == current_user.id,
            func.date(Entry.created_at) == today
        )
    )
    is_premium = current_user.is_subscribed and current_user.subscription_expires and current_user.subscription_expires > datetime.utcnow()
    return {
        "count": count or 0,
        "limit": 999 if is_premium else 3,
        "is_premium": is_premium
    }