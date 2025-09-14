"""merge multiple heads

Revision ID: 5f58ff0755f4
Revises: 16882f9cb8bf, 3ce7adcbc68f
Create Date: 2025-09-15 01:48:46.336839

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f58ff0755f4'
down_revision: Union[str, Sequence[str], None] = ('16882f9cb8bf', '3ce7adcbc68f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
