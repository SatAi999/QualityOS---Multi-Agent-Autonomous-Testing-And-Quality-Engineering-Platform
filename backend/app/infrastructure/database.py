from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings
from app.domain.models import Base

# Sync Engine and Session for migrations or legacy sync paths
sync_engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Async Engine and Session for FastAPI and async runs
async_engine = create_async_engine(settings.ASYNC_SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def init_db() -> None:
    """Initialize DB and create tables if they do not exist."""
    async with async_engine.begin() as conn:
        # For development, automatically build schemas. 
        # In a real enterprise env, we'd use Alembic migrations.
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Dependency for retrieving async DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
