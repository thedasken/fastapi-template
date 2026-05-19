from sqlalchemy import Column, DateTime, Integer, String, Table, Text
from sqlalchemy.sql import func

from src.database import metadata

items = Table(
    "item",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(length=255), nullable=False),
    Column("description", Text, nullable=True),
    Column(
        "created_at", DateTime(timezone=True), server_default=func.now(), nullable=False
    ),
)
