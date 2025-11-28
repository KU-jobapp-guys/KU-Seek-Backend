"""Merge login-rate-limit to main

Revision ID: 4d28aca67b2c
Revises: cc801902a3e1, f4973c8f4b51
Create Date: 2025-11-27 22:54:42.739311

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d28aca67b2c'
down_revision: Union[str, Sequence[str], None] = ('cc801902a3e1', 'f4973c8f4b51')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
