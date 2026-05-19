from typing import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from src.config import settings
from src.constants import DB_NAMING_CONVENTION

DATABASE_URL = str(settings.DATABASE_ASYNC_URL)

engine = create_async_engine(
    DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    pool_recycle=settings.DATABASE_POOL_TTL,
    pool_pre_ping=settings.DATABASE_POOL_PRE_PING,
)
metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)


async def get_db_connection() -> AsyncGenerator[AsyncConnection, None]:
    async with engine.begin() as connection:
        yield connection


from src.items import models as items_models  # noqa: E402, F401
