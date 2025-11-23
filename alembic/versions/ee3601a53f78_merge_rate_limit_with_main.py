"""Merge rate_limit with main

Revision ID: ee3601a53f78
Revises: 294113370424, a917aeacea96
Create Date: 2025-11-23 03:00:26.700784

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee3601a53f78'
down_revision: Union[str, Sequence[str], None] = ('294113370424', 'a917aeacea96')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
