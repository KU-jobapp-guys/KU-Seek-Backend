"""merge tos model to main

Revision ID: 0249c31c09dd
Revises: 294113370424, a917aeacea96
Create Date: 2025-11-20 08:06:54.106489

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0249c31c09dd'
down_revision: Union[str, Sequence[str], None] = ('294113370424', 'a917aeacea96')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
