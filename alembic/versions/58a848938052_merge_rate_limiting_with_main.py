"""Merge rate-limiting with main

Revision ID: 58a848938052
Revises: 336884f6fc01, ee3601a53f78
Create Date: 2025-11-23 20:35:57.126707

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '58a848938052'
down_revision: Union[str, Sequence[str], None] = ('336884f6fc01', 'ee3601a53f78')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
