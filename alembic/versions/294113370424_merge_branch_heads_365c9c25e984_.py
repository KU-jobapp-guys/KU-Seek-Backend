"""merge branch heads 365c9c25e984 + de4a49cd28ed

Revision ID: 294113370424
Revises: 365c9c25e984, de4a49cd28ed
Create Date: 2025-11-19 21:15:05.730155

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '294113370424'
down_revision: Union[str, Sequence[str], None] = ('365c9c25e984', 'de4a49cd28ed')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
