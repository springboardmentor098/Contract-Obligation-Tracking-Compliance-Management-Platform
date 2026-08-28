"""create renewals table

Revision ID: 82ad8ba139b0
Revises: c509bc03e6d0
Create Date: 2026-08-28 15:37:53.154692

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '82ad8ba139b0'
down_revision: Union[str, Sequence[str], None] = 'c509bc03e6d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema by recreating renewals table to match Sprint 10 structure."""
    op.execute("DROP TABLE IF EXISTS renewals CASCADE")
    op.create_table(
        'renewals',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('renewal_date', sa.Date(), nullable=True),
        sa.Column('previous_expiry_date', sa.Date(), nullable=True),
        sa.Column('new_expiry_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Upcoming'),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.user_id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_renewals_id'), 'renewals', ['id'], unique=False)
    op.create_index(op.f('ix_renewals_contract_id'), 'renewals', ['contract_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_renewals_contract_id'), table_name='renewals')
    op.drop_index(op.f('ix_renewals_id'), table_name='renewals')
    op.drop_table('renewals')
