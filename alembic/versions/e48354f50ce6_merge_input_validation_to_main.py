"""Merge input-validation to main

Revision ID: e48354f50ce6
Revises: 83876f877056, cc801902a3e1
Create Date: 2025-11-27 23:23:00.599387

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e48354f50ce6'
down_revision: Union[str, Sequence[str], None] = ('83876f877056', 'cc801902a3e1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
