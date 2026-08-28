"""add compliance monitoring

Revision ID: 78588cf4b962
Revises: cfdbb006a94e
Create Date: 2026-08-28 15:35:16.312090
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '78588cf4b962'
down_revision: Union[str, Sequence[str], None] = 'cfdbb006a94e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'compliance_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('compliance_score', sa.Integer(), nullable=False),
        sa.Column('risk_level', sa.String(length=50), nullable=False),
        sa.Column(
            'evaluated_at',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ['contract_id'],
            ['contracts.id']
        ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_compliance_records_id'),
        'compliance_records',
        ['id'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(
        op.f('ix_compliance_records_id'),
        table_name='compliance_records'
    )

    op.drop_table('compliance_records')