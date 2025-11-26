"""merging mail tables with head branch

Revision ID: 336884f6fc01
Revises: 294113370424, cfdb9c54cfab
Create Date: 2025-11-22 18:58:52.552399

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '336884f6fc01'
down_revision: Union[str, Sequence[str], None] = ('294113370424', 'cfdb9c54cfab')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
