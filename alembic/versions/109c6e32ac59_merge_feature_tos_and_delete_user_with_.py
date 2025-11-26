"""Merge feature/tos-and-delete-user with main

Revision ID: 109c6e32ac59
Revises: 0249c31c09dd, 336884f6fc01
Create Date: 2025-11-23 20:51:47.584371

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '109c6e32ac59'
down_revision: Union[str, Sequence[str], None] = ('0249c31c09dd', '336884f6fc01')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
