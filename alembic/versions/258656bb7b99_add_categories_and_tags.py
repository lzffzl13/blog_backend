"""add categories and tags

Revision ID: 258656bb7b99
Revises: 001
Create Date: 2026-05-31 11:10:59.701949

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "258656bb7b99"
down_revision: str | Sequence[str] | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ARTICLE_CATEGORY_FK = "fk_articles_category_id_categories"


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False, comment="分类名称"),
        sa.Column("description", sa.String(length=255), nullable=True, comment="分类描述"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_categories_id"), "categories", ["id"], unique=False)

    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=30), nullable=False, comment="标签名称"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_tags_id"), "tags", ["id"], unique=False)

    op.add_column("articles", sa.Column("category_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        ARTICLE_CATEGORY_FK,
        "articles",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "article_tags",
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("article_id", "tag_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("article_tags")
    op.drop_constraint(ARTICLE_CATEGORY_FK, "articles", type_="foreignkey")
    op.drop_column("articles", "category_id")
    op.drop_index(op.f("ix_tags_id"), table_name="tags")
    op.drop_table("tags")
    op.drop_index(op.f("ix_categories_id"), table_name="categories")
    op.drop_table("categories")
