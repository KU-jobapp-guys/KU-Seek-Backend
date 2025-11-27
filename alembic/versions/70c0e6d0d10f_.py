"""empty message

Revision ID: 70c0e6d0d10f
Revises: cc801902a3e1, cf0444674ccc
Create Date: 2025-11-28 01:29:03.112383

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '70c0e6d0d10f'
down_revision: Union[str, Sequence[str], None] = ('cc801902a3e1', 'cf0444674ccc')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
