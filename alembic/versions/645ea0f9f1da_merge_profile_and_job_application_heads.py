"""merge profile and job application heads

Revision ID: 645ea0f9f1da
Revises: 57b56a7b8bbe, 98429113644f
Create Date: 2025-10-13 19:36:47.983184

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '645ea0f9f1da'
down_revision: Union[str, Sequence[str], None] = ('57b56a7b8bbe', '98429113644f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
