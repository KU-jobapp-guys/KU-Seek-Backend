"""Merge InputValidation to main

Revision ID: 83876f877056
Revises: 109c6e32ac59, 58a848938052
Create Date: 2025-11-27 21:40:39.275529

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '83876f877056'
down_revision: Union[str, Sequence[str], None] = ('109c6e32ac59', '58a848938052')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
