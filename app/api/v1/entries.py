from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.core.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.core.config import settings  # Если нет settings, используй os.getenv
import httpx
import os

router = APIRouter(prefix="/entries", tags=["entries"])

# Токен твоего бота (прописан напрямую)
BOT_TOKEN = "8796483021:AAEBlUMP6e-2JWbfopilvA8fJB1fpZj0Pzw"
# Твой Telegram ID (прописан напрямую)
ADMIN_ID = "8796483021"

@router.post("/confirm-payment")
async def request_payment_confirmation(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Отправляем уведомление админу с кнопкой подтверждения
    async with httpx.AsyncClient() as client:
        # Сначала отправляем сообщение админу
        await client.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": ADMIN_ID,
                "text": f"🛒 Пользователь @{current_user.username or 'None'} (ID: {current_user.id}) нажал кнопку «Я оплатил».\n\nПожалуйста, проверьте перевод и подтвердите оплату:",
                "reply_markup": {
                    "inline_keyboard": [[
                        {"text": "✅ Подтвердить", "callback_data": f"confirm_{current_user.id}"},
                        {"text": "❌ Отклонить", "callback_data": f"reject_{current_user.id}"}
                    ]]
                }
            }
        )

    return {"status": "pending", "message": "Уведомление отправлено админу"}