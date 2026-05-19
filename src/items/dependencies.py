from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncConnection

from src.database import get_db_connection
from src.items import service


async def valid_item_id(
    item_id: int,
    conn: Annotated[AsyncConnection, Depends(get_db_connection)],
) -> dict:
    return await service.get_item_by_id(item_id, conn)
