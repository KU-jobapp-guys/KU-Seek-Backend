"""merge heads

Revision ID: de4a49cd28ed
Revises: 04398c34e35f, 05987fc55dc6
Create Date: 2025-11-08 00:41:58.436385

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de4a49cd28ed'
down_revision: Union[str, Sequence[str], None] = ('04398c34e35f', '05987fc55dc6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
