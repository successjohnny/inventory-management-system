"""populate normalized product names

Revision ID: 4bf96d1a5659
Revises: c45f08a4e27c
Create Date: 2026-09-14 14:41:29.436710

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4bf96d1a5659'
down_revision: Union[str, Sequence[str], None] = 'c45f08a4e27c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Populate normalized product names."""

    op.execute(
        "UPDATE products "
        "SET normalized_name = lower(trim(name))"
    )


def downgrade() -> None:
    """Nothing to reverse."""

    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
