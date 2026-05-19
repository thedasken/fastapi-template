from datetime import datetime

from pydantic import Field

from src.schemas import CustomModel


class ItemCreate(CustomModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None


class ItemUpdate(CustomModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None


class ItemResponse(CustomModel):
    id: int
    title: str
    description: str | None
    created_at: datetime
