import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./mooddiary.db")

# Async engine for the application (то, что использует FastAPI)
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

# Sync engine for table creation (обходит ошибку AsyncEngine)
sync_engine = create_engine(DATABASE_URL.replace("+aiosqlite", ""))

async def get_db():
    async with async_session() as session:
        yield session
