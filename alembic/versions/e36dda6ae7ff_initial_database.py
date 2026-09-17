"""initial database

Revision ID: e36dda6ae7ff
Revises:
Create Date: 2026-09-14 10:31:04.890107

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision: str = "e36dda6ae7ff"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the original inventory database tables."""

    op.create_table(
        "products",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False,
        ),

        sa.Column(
            "name",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "price",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "quantity",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "low_stock_level",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "category",
            sa.String(),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_products_id",
        "products",
        ["id"],
        unique=False,
    )

    op.create_table(
        "stock_movements",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False,
        ),

        sa.Column(
            "product_id",
            sa.Integer(),
            sa.ForeignKey("products.id"),
            nullable=False,
        ),

        sa.Column(
            "movement_type",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "quantity",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "note",
            sa.String(),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_stock_movements_id",
        "stock_movements",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove the original inventory database tables."""

    op.drop_index(
        "ix_stock_movements_id",
        table_name="stock_movements",
    )

    op.drop_table("stock_movements")

    op.drop_index(
        "ix_products_id",
        table_name="products",
    )

    op.drop_table("products")