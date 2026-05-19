from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine
from sqlalchemy.pool import NullPool

from src.config import settings
from src.database import get_db_connection
from src.main import app

# NullPool avoids asyncpg connections being reused across event loops between tests.
_test_engine = create_async_engine(str(settings.DATABASE_ASYNC_URL), poolclass=NullPool)


@pytest.fixture
async def db_conn() -> AsyncGenerator[AsyncConnection, None]:
    """Yield a connection whose transaction is rolled back after the test."""
    async with _test_engine.connect() as conn:
        transaction = await conn.begin()
        yield conn
        await transaction.rollback()


@pytest.fixture
async def client(db_conn: AsyncConnection) -> AsyncGenerator[AsyncClient, None]:
    """AsyncClient wired to the app with get_db_connection overridden to use
    the test transaction so all DB writes are rolled back after each test."""

    async def override_get_db_connection():
        yield db_conn

    app.dependency_overrides[get_db_connection] = override_get_db_connection
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac
    finally:
        del app.dependency_overrides[get_db_connection]
