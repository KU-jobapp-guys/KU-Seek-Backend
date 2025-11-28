"""Merge login-rate-limit with main

Revision ID: f4973c8f4b51
Revises: 109c6e32ac59, 58a848938052
Create Date: 2025-11-26 22:08:44.479292

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4973c8f4b51'
down_revision: Union[str, Sequence[str], None] = ('109c6e32ac59', '58a848938052')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
