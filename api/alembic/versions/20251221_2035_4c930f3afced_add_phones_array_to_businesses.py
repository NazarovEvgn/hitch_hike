"""add phones array to businesses

Revision ID: 4c930f3afced
Revises: 9h0c1d2e3f4g
Create Date: 2025-12-21 20:35:20.792970

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '4c930f3afced'
down_revision: Union[str, None] = '9h0c1d2e3f4g'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add phones column as JSON array
    op.add_column('businesses', sa.Column('phones', postgresql.JSON(astext_type=sa.Text()), nullable=True))

    # Migrate data: copy phone to phones as array
    op.execute("""
        UPDATE businesses
        SET phones = json_build_array(phone)
        WHERE phone IS NOT NULL
    """)

    # Make phones NOT NULL with default empty array
    op.alter_column('businesses', 'phones', nullable=False, server_default='[]')

    # Drop old phone column
    op.drop_column('businesses', 'phone')


def downgrade() -> None:
    # Add back phone column
    op.add_column('businesses', sa.Column('phone', sa.String(20), nullable=True))

    # Migrate data: take first phone from phones array
    op.execute("""
        UPDATE businesses
        SET phone = phones->>0
        WHERE phones IS NOT NULL AND json_array_length(phones) > 0
    """)

    # Make phone NOT NULL
    op.alter_column('businesses', 'phone', nullable=False)

    # Drop phones column
    op.drop_column('businesses', 'phones')
