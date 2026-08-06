from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User
from datetime import datetime, timedelta

router = APIRouter(prefix="/subscription", tags=["subscription"])

# Существующий эндпоинт /status и /buy (если есть) — оставляем
# Добавляем новый:

@router.post("/activate-by-telegram")
async def activate_by_telegram(
    telegram_id: int,
    db: AsyncSession = Depends(get_db)
):
    # Ищем пользователя по telegram_id
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Активируем подписку на 30 дней
    user.is_subscribed = True
    user.subscription_expires = datetime.utcnow() + timedelta(days=30)
    await db.commit()
    await db.refresh(user)
    
    return {"message": "Subscription activated", "expires": user.subscription_expires.isoformat()}