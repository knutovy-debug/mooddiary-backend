from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.database import get_db
from app.models.entry import Entry
from app.models.user import User
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/entries", tags=["entries"])
from collections import Counter

@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Entry)
        .where(Entry.user_id == current_user.id)
        .order_by(Entry.created_at)
    )
    entries = result.scalars().all()
    
    if not entries:
        return {"dates": [], "sentiments": [], "stress": [], "topics": {}}
    
    dates = [e.created_at.strftime("%Y-%m-%d") for e in entries]
    # Преобразуем настроение в числа: positive=1, neutral=0, negative=-1
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