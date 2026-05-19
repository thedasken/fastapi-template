"""create_item_table

Revision ID: afa2a1fb5fad
Revises:
Create Date: 2026-05-19 12:13:41.346731

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "afa2a1fb5fad"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("item_pkey")),
    )


def downgrade() -> None:
    op.drop_table("item")
