from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["auth"])

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await db.execute(select(User).where(User.email == data.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Пользователь с такой почтой уже существует")
    
    new_user = User(email=data.email, hashed_password=hash_password(data.password), is_subscribed=False)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    token = create_access_token({"sub": str(new_user.id)})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login")
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).where(User.email == data.email))
    user = user.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверная почта или пароль")
    
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}
