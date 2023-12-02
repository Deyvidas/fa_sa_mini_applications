"""Initial migration

Revision ID: 485c0e5953a7
Revises: 
Create Date: 2023-12-02 08:47:24.669556

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '485c0e5953a7'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def downgrade() -> None:
    op.drop_table('balance')
    op.drop_table('transaction')
    op.drop_table('client')
    op.drop_table('status_desc')
    op.drop_table('card')


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
        sa.Column('client_id', sa.INTEGER(), server_default=sa.text("nextval('client_client_id_seq'::regclass)"), autoincrement=True, nullable=False),
        sa.Column('full_name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column('reg_date', sa.DATE(), autoincrement=False, nullable=False),
        sa.Column('doc_num', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
        sa.Column('doc_series', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
        sa.Column('phone', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
        sa.Column('VIP_flag', sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column('birth_date', sa.DATE(), autoincrement=False, nullable=False),
        sa.Column('sex', postgresql.ENUM('MALE', 'FEMALE', name='sex'), autoincrement=False, nullable=False),
        sa.Column('status', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['status'], ['status_desc.status'], name='client_status_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('client_id', name='client_pkey'),
        postgresql_ignore_search_path=False
    )
    op.create_table(
        'balance',
        sa.Column('row_id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('current_amount', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False),
        sa.Column('actual_flag', sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column('processed_datetime', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column('client_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['client.client_id'], name='balance_client_id_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('row_id', name='balance_pkey')
    )
    op.create_table(
        'card',
        sa.Column('card_number', sa.VARCHAR(length=16), autoincrement=False, nullable=False),
        sa.Column('card_type', postgresql.ENUM('DEBIT', 'CREDIT', name='cardtype'), autoincrement=False, nullable=False),
        sa.Column('open_date', sa.DATE(), autoincrement=False, nullable=False),
        sa.Column('close_date', sa.DATE(), autoincrement=False, nullable=False),
        sa.Column('processed_datetime', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column('client_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['client.client_id'], name='card_client_id_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('card_number', name='card_pkey'),
        postgresql_ignore_search_path=False
    )
    op.create_table(
        'transaction',
        sa.Column('trans_id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('trans_amount', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False),
        sa.Column('trans_datetime', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column('processed_datetime', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column('card_number', sa.VARCHAR(length=16), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['card_number'], ['card.card_number'], name='transaction_card_number_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('trans_id', name='transaction_pkey')
    )
