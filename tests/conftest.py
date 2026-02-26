import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.app.core.db.database import DATABASE_URL, async_get_db
from src.app.main import app


@pytest_asyncio.fixture(scope="function")
async def engine():
    engine = create_async_engine(DATABASE_URL, echo=False, future=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db_session(engine):
    async with engine.connect() as connection:
        await connection.begin()

        session_factory = async_sessionmaker(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        async with session_factory() as session:
            yield session
            await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def patched_app(test_db_session):
    async def override_dependency():
        yield test_db_session

    app.dependency_overrides[async_get_db] = override_dependency
    yield app
    app.dependency_overrides.pop(async_get_db)


@pytest_asyncio.fixture(scope="function")
async def client(patched_app):
    async with AsyncClient(transport=ASGITransport(app=patched_app), base_url="http://testserver") as ac:
        yield ac
    await ac.aclose()
