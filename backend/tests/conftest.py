import asyncio
import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.infrastructure.database import get_db
from app.domain.models import Base
from app.main import app as fastapi_app
from httpx import AsyncClient, ASGITransport

# Test Database URI (async SQLite in-memory)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

import app.infrastructure.database
app.infrastructure.database.AsyncSessionLocal = TestSessionLocal

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    """Initializes in-memory test schemas."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    # Dispose engine to close connections and prevent pytest from hanging in the background
    await test_engine.dispose()

@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Provides a fresh transactional test database session."""
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

@pytest.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provides an HTTPX AsyncClient with overridden database dependencies."""
    async def override_get_db():
        try:
            yield db
        finally:
            pass
            
    fastapi_app.dependency_overrides[get_db] = override_get_db
    # Using modern HTTPX 0.27+ ASGITransport construction
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as ac:
        yield ac
    fastapi_app.dependency_overrides.clear()
