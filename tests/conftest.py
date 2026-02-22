from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.app.core.db.database import DATABASE_URL, async_get_db
from src.app.main import app

engine = create_async_engine(DATABASE_URL)
TestingSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture
async def db_session():
    """Provides a transactional session that rolls back after every test."""
    async with engine.connect() as connection:
        await connection.begin()
        async with TestingSessionLocal(bind=connection).begin() as session:
            yield session
            await session.rollback()


@pytest_asyncio.fixture
async def client(db_session):
    """Provides an AsyncClient with the DB dependency overridden."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[async_get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def mock_redis():
    """Mock Redis connection for unit tests."""
    mock_redis = Mock()
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.delete = AsyncMock(return_value=True)
    return mock_redis
