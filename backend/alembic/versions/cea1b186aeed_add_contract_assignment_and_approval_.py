"""add contract assignment and approval fields

Revision ID: cea1b186aeed
Revises: cc61b70c7370
Create Date: 2026-08-19 15:32:20.168393

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cea1b186aeed'
down_revision: Union[str, Sequence[str], None] = 'cc61b70c7370'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        'contracts',
        sa.Column(
            'assigned_to',
            sa.Integer(),
            nullable=True
        )
    )

    op.add_column(
        'contracts',
        sa.Column(
            'reviewed_at',
            sa.DateTime(),
            nullable=True
        )
    )

    op.add_column(
        'contracts',
        sa.Column(
            'approved_at',
            sa.DateTime(),
            nullable=True
        )
    )

    op.create_foreign_key(
        'fk_contracts_assigned_to_users',
        'contracts',
        'users',
        ['assigned_to'],
        ['id']
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        'fk_contracts_assigned_to_users',
        'contracts',
        type_='foreignkey'
    )

    op.drop_column('contracts', 'approved_at')
    op.drop_column('contracts', 'reviewed_at')
    op.drop_column('contracts', 'assigned_to')