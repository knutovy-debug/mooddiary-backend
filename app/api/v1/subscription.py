from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from datetime import datetime, timedelta

router = APIRouter(prefix="/subscription", tags=["subscription"])

@router.get("/status")
async def get_subscription_status(
    current_user: User = Depends(get_current_user)
):
    if current_user.is_subscribed and current_user.subscription_expires and current_user.subscription_expires > datetime.utcnow():
        return {"is_subscribed": True, "expires": current_user.subscription_expires.isoformat()}
    return {"is_subscribed": False}

@router.post("/activate-by-telegram")
async def activate_by_telegram(
    telegram_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_subscribed = True
    user.subscription_expires = datetime.utcnow() + timedelta(days=30)
    await db.commit()
    return {"message": "Subscription activated", "expires": user.subscription_expires.isoformat()}