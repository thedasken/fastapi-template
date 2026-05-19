import logging

from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncConnection

from src.items.exceptions import ItemNotFound
from src.items.models import items
from src.items.schemas import ItemCreate, ItemUpdate

logger = logging.getLogger(__name__)


async def get_item_by_id(item_id: int, conn: AsyncConnection) -> dict:
    query = select(items).where(items.c.id == item_id)
    result = await conn.execute(query)
    row = result.mappings().first()
    if row is None:
        logger.info("Item not found", extra={"item_id": item_id})
        raise ItemNotFound()
    return dict(row)


async def list_items(
    conn: AsyncConnection, *, limit: int = 50, offset: int = 0
) -> tuple[list[dict], int]:
    items_query = (
        select(items).limit(limit).offset(offset).order_by(items.c.created_at.desc())
    )
    # NOTE: if you add WHERE conditions to items_query, replicate them here
    count_query = select(func.count()).select_from(items)
    items_result = await conn.execute(items_query)
    count_result = await conn.execute(count_query)
    return [
        dict(row) for row in items_result.mappings().all()
    ], count_result.scalar_one()


async def create_item(data: ItemCreate, conn: AsyncConnection) -> dict:
    query = insert(items).values(**data.model_dump()).returning(items)
    result = await conn.execute(query)
    row = result.mappings().first()
    # Should always return a row, but explicit check for Pylance
    if row is None:
        raise RuntimeError("Item creation did not return a row")
    item = dict(row)
    logger.info("Item created", extra={"item_id": item["id"]})
    return item


async def update_item(item_id: int, data: ItemUpdate, conn: AsyncConnection) -> dict:
    payload = data.model_dump(exclude_unset=True)
    query = (
        update(items).where(items.c.id == item_id).values(**payload).returning(items)
    )
    result = await conn.execute(query)
    row = result.mappings().first()
    if row is None:
        logger.info("Item not found during update", extra={"item_id": item_id})
        raise ItemNotFound()
    item = dict(row)
    logger.info("Item updated", extra={"item_id": item_id, "fields": sorted(payload)})
    return item


async def delete_item(item_id: int, conn: AsyncConnection) -> None:
    query = delete(items).where(items.c.id == item_id)
    result = await conn.execute(query)
    if result.rowcount == 0:
        logger.info("Item not found during delete", extra={"item_id": item_id})
        raise ItemNotFound()
    logger.info("Item deleted", extra={"item_id": item_id})
