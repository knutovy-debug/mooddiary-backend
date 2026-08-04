from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.user import UserCreate, UserLogin

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = get_password_hash(user_data.password)
    new_user = User(email=user_data.email, hashed_password=hashed)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"message": "User created", "user_id": new_user.id}

@router.post("/login")
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}