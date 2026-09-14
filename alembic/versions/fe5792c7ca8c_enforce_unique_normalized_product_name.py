"""enforce unique normalized product name

Revision ID: fe5792c7ca8c
Revises: 4bf96d1a5659
Create Date: 2026-09-14 14:56:23.232278

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fe5792c7ca8c'
down_revision: Union[str, Sequence[str], None] = '4bf96d1a5659'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Enforce normalized product name constraints."""

    with op.batch_alter_table("products") as batch_op:

        batch_op.alter_column(
            "normalized_name",
            existing_type=sa.String(),
            nullable=False,
        )

        batch_op.create_unique_constraint(
            "uq_products_normalized_name",
            ["normalized_name"],
        )


def downgrade() -> None:
    """Remove normalized product name constraints."""

    with op.batch_alter_table("products") as batch_op:

        batch_op.drop_constraint(
            "uq_products_normalized_name",
            type_="unique",
        )

        batch_op.alter_column(
            "normalized_name",
            existing_type=sa.String(),
            nullable=True,
        )
