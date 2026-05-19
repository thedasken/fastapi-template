from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncConnection

from src.database import get_db_connection
from src.items import service
from src.items.dependencies import valid_item_id
from src.items.schemas import ItemCreate, ItemResponse, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[ItemResponse])
async def list_items(
    conn: Annotated[AsyncConnection, Depends(get_db_connection)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return await service.list_items(conn, limit=limit, offset=offset)


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item: Annotated[dict, Depends(valid_item_id)]):
    return item


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    data: ItemCreate,
    conn: Annotated[AsyncConnection, Depends(get_db_connection)],
):
    return await service.create_item(data, conn)


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(
    item: Annotated[dict, Depends(valid_item_id)],
    data: ItemUpdate,
    conn: Annotated[AsyncConnection, Depends(get_db_connection)],
):
    return await service.update_item(item["id"], data, conn)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item: Annotated[dict, Depends(valid_item_id)],
    conn: Annotated[AsyncConnection, Depends(get_db_connection)],
):
    await service.delete_item(item["id"], conn)
