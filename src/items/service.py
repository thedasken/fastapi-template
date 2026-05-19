from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncConnection

from src.items.exceptions import ItemNotFound
from src.items.models import items
from src.items.schemas import ItemCreate, ItemUpdate


async def get_item_by_id(item_id: int, conn: AsyncConnection) -> dict:
    query = select(items).where(items.c.id == item_id)
    result = await conn.execute(query)
    row = result.mappings().first()
    if row is None:
        raise ItemNotFound()
    return dict(row)


async def list_items(
    conn: AsyncConnection, *, limit: int = 50, offset: int = 0
) -> list[dict]:
    query = (
        select(items).limit(limit).offset(offset).order_by(items.c.created_at.desc())
    )
    result = await conn.execute(query)
    return [dict(row) for row in result.mappings().all()]


async def create_item(data: ItemCreate, conn: AsyncConnection) -> dict:
    query = insert(items).values(**data.model_dump()).returning(items)
    result = await conn.execute(query)
    return dict(result.mappings().first())


async def update_item(item_id: int, data: ItemUpdate, conn: AsyncConnection) -> dict:
    payload = data.model_dump(exclude_unset=True)
    if not payload:
        return await get_item_by_id(item_id, conn)
    query = (
        update(items).where(items.c.id == item_id).values(**payload).returning(items)
    )
    result = await conn.execute(query)
    row = result.mappings().first()
    if row is None:
        raise ItemNotFound()
    return dict(row)


async def delete_item(item_id: int, conn: AsyncConnection) -> None:
    query = delete(items).where(items.c.id == item_id)
    result = await conn.execute(query)
    if result.rowcount == 0:
        raise ItemNotFound()
