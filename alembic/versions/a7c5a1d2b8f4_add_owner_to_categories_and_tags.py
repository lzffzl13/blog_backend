"""add owner to categories and tags

Revision ID: a7c5a1d2b8f4
Revises: 4b7a6f0d8c21
Create Date: 2026-06-14 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a7c5a1d2b8f4"
down_revision: str | Sequence[str] | None = "4b7a6f0d8c21"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("categories", sa.Column("owner_id", sa.Integer(), nullable=True))
    op.add_column("tags", sa.Column("owner_id", sa.Integer(), nullable=True))

    op.execute("UPDATE categories SET owner_id = (SELECT id FROM users ORDER BY id LIMIT 1)")
    op.execute("UPDATE tags SET owner_id = (SELECT id FROM users ORDER BY id LIMIT 1)")

    op.alter_column("categories", "owner_id", nullable=False)
    op.alter_column("tags", "owner_id", nullable=False)

    op.create_foreign_key(
        "fk_categories_owner_id_users",
        "categories",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_tags_owner_id_users",
        "tags",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_tags_owner_id_users", "tags", type_="foreignkey")
    op.drop_constraint("fk_categories_owner_id_users", "categories", type_="foreignkey")
    op.drop_column("tags", "owner_id")
    op.drop_column("categories", "owner_id")
