"""Change FK to use correct id (change from users.id to professors.id, companies.id, students.id)

Revision ID: 98429113644f
Revises: b0502db5e9f7
Create Date: 2025-10-07 23:10:32.606167

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '98429113644f'
down_revision: Union[str, Sequence[str], None] = 'b0502db5e9f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Announcements table
    op.drop_constraint('announcements_ibfk_1', 'announcements', type_='foreignkey')
    op.alter_column('announcements', 'professor_id',
               existing_type=mysql.CHAR(length=32),
               type_=sa.Integer(),
               existing_nullable=False)
    op.create_foreign_key(None, 'announcements', 'professors', ['professor_id'], ['id'], ondelete='CASCADE')
    
    # Professor connections table
    op.drop_constraint('professor_connections_ibfk_1', 'professor_connections', type_='foreignkey')
    op.drop_constraint('professor_connections_ibfk_2', 'professor_connections', type_='foreignkey')
    op.alter_column('professor_connections', 'professor_id',
               existing_type=mysql.CHAR(length=32),
               type_=sa.Integer(),
               existing_nullable=False)
    op.alter_column('professor_connections', 'company_id',
               existing_type=mysql.CHAR(length=32),
               type_=sa.Integer(),
               existing_nullable=False)
    op.create_foreign_key(None, 'professor_connections', 'companies', ['company_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'professor_connections', 'professors', ['professor_id'], ['id'], ondelete='CASCADE')
    
    # Student documents table
    op.drop_constraint('student_documents_ibfk_1', 'student_documents', type_='foreignkey')
    op.alter_column('student_documents', 'student_id',
               existing_type=mysql.CHAR(length=32),
               type_=sa.Integer(),
               existing_nullable=False)
    op.create_foreign_key(None, 'student_documents', 'students', ['student_id'], ['id'], ondelete='CASCADE')
    
    # Student histories table
    op.drop_constraint('student_histories_ibfk_2', 'student_histories', type_='foreignkey')
    op.alter_column('student_histories', 'student_id',
               existing_type=mysql.CHAR(length=32),
               type_=sa.Integer(),
               existing_nullable=False)
    op.create_foreign_key(None, 'student_histories', 'students', ['student_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """Downgrade schema."""
    # Student histories table
    op.drop_constraint(None, 'student_histories', type_='foreignkey')
    op.alter_column('student_histories', 'student_id',
               existing_type=sa.Integer(),
               type_=mysql.CHAR(length=32),
               existing_nullable=False)
    op.create_foreign_key('student_histories_ibfk_2', 'student_histories', 'users', ['student_id'], ['id'], ondelete='CASCADE')
    
    # Student documents table
    op.drop_constraint(None, 'student_documents', type_='foreignkey')
    op.alter_column('student_documents', 'student_id',
               existing_type=sa.Integer(),
               type_=mysql.CHAR(length=32),
               existing_nullable=False)
    op.create_foreign_key('student_documents_ibfk_1', 'student_documents', 'users', ['student_id'], ['id'], ondelete='CASCADE')
    
    # Professor connections table
    op.drop_constraint(None, 'professor_connections', type_='foreignkey')
    op.drop_constraint(None, 'professor_connections', type_='foreignkey')
    op.alter_column('professor_connections', 'company_id',
               existing_type=sa.Integer(),
               type_=mysql.CHAR(length=32),
               existing_nullable=False)
    op.alter_column('professor_connections', 'professor_id',
               existing_type=sa.Integer(),
               type_=mysql.CHAR(length=32),
               existing_nullable=False)
    op.create_foreign_key('professor_connections_ibfk_1', 'professor_connections', 'users', ['company_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('professor_connections_ibfk_2', 'professor_connections', 'users', ['professor_id'], ['id'], ondelete='CASCADE')
    
    # Announcements table
    op.drop_constraint(None, 'announcements', type_='foreignkey')
    op.alter_column('announcements', 'professor_id',
               existing_type=sa.Integer(),
               type_=mysql.CHAR(length=32),
               existing_nullable=False)
    op.create_foreign_key('announcements_ibfk_1', 'announcements', 'users', ['professor_id'], ['id'], ondelete='CASCADE')