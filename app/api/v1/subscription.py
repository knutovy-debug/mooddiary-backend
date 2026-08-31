from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from datetime import datetime, timedelta
from yookassa import Configuration, Payment
import os

router = APIRouter(prefix="/subscription", tags=["subscription"])

@router.get("/status")
async def get_subscription_status(
    current_user: User = Depends(get_current_user)
):
    if current_user.is_subscribed and current_user.subscription_expires and current_user.subscription_expires > datetime.utcnow():
        return {
            "is_subscribed": True,
            "expires": current_user.subscription_expires.isoformat()
        }
    return {"is_subscribed": False}

@router.post("/activate-by-telegram")
async def activate_by_telegram(
    telegram_id: int,
    amount: int,
    period: str,
    db: AsyncSession = Depends(get_db)
):
    # Ищем пользователя в базе
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Настраиваем ЮKassa (ключи жёстко, чтобы не зависеть от .env)
    Configuration.account_id = "1428888"
    Configuration.secret_key = "live_a7oa8ZsGDfyUFvogRDD-FYbQcnJbB44YoTgKkJzn8Z8"  # замени, если ключ другой

    # Создаём платёж через библиотеку yookassa
    try:
        payment = Payment.create({
            "amount": {
                "value": float(amount),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://mooddiary-frontend-zeta.vercel.app"
            },
            "description": f"Подписка на {period} для пользователя {telegram_id}",
            "metadata": {
                "telegram_id": telegram_id,
                "period": period
            }
        })
        
        # Возвращаем боту ссылку на оплату
        return {
            "confirmation_url": payment.confirmation.confirmation_url
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))