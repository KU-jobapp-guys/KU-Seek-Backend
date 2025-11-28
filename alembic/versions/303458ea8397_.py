"""empty message

Revision ID: 303458ea8397
Revises: 9e5426c3a0d1, cc801902a3e1
Create Date: 2025-11-27 23:20:42.310771

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '303458ea8397'
down_revision: Union[str, Sequence[str], None] = ('9e5426c3a0d1', 'cc801902a3e1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
