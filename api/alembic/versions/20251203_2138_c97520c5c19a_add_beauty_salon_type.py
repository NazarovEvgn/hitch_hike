"""add_beauty_salon_type

Revision ID: c97520c5c19a
Revises: 40f791c73a0e
Create Date: 2025-12-03 21:38:22.412473

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c97520c5c19a'
down_revision: Union[str, None] = '40f791c73a0e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new value to BusinessType enum
    op.execute("ALTER TYPE businesstype ADD VALUE IF NOT EXISTS 'beauty_salon'")


def downgrade() -> None:
    # Note: PostgreSQL does not support removing enum values directly
    # Manual intervention required if downgrade is needed
    pass
