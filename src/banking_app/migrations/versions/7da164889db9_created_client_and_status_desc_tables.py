"""Created client and status_desc tables.

Revision ID: 7da164889db9
Revises: 
Create Date: 2023-12-02 00:40:28.932545

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7da164889db9'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def downgrade() -> None:
    op.drop_table('client')
    op.drop_table('status_desc')


def upgrade() -> None:
    op.create_table(
        'status_desc',
        sa.Column('status', sa.INTEGER(), server_default=sa.text("nextval('status_desc_status_seq'::regclass)"), autoincrement=True, nullable=False),
        sa.Column('description', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint('status', name='status_desc_pkey'),
        postgresql_ignore_search_path=False
    )
    op.create_table(
        'client',
        sa.Column('client_id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('full_name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column('reg_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column('doc_num', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
        sa.Column('doc_series', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
        sa.Column('phone', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
        sa.Column('VIP_flag', sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column('birth_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column('sex', postgresql.ENUM('MALE', 'FEMALE', name='sex'), autoincrement=False, nullable=False),
        sa.Column('status', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['status'], ['status_desc.status'], name='client_status_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('client_id', name='client_pkey')
    )
