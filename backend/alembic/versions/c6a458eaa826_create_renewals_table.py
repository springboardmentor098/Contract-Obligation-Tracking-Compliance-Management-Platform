"""create renewals table

Revision ID: c6a458eaa826
Revises: 7ef242994096
Create Date: 2026-08-27 20:53:33.335370

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c6a458eaa826'
down_revision: Union[str, Sequence[str], None] = '7ef242994096'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        'renewals',
        sa.Column(
            'previous_expiry_date',
            sa.Date(),
            nullable=False
        )
    )

    op.add_column(
        'renewals',
        sa.Column(
            'new_expiry_date',
            sa.Date(),
            nullable=True
        )
    )

    op.add_column(
        'renewals',
        sa.Column(
            'assigned_to',
            sa.Integer(),
            nullable=True
        )
    )

    op.add_column(
        'renewals',
        sa.Column(
            'notes',
            sa.String(length=1000),
            nullable=True
        )
    )

    op.add_column(
        'renewals',
        sa.Column(
            'created_at',
            sa.DateTime(),
            nullable=False
        )
    )

    op.add_column(
        'renewals',
        sa.Column(
            'updated_at',
            sa.DateTime(),
            nullable=False
        )
    )

    op.create_foreign_key(
        'fk_renewals_assigned_to_users',
        'renewals',
        'users',
        ['assigned_to'],
        ['id']
    )  
def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        'fk_renewals_assigned_to_users',
        'renewals',
        type_='foreignkey'
    )

    op.drop_column(
        'renewals',
        'updated_at'
    )

    op.drop_column(
        'renewals',
        'created_at'
    )

    op.drop_column(
        'renewals',
        'notes'
    )

    op.drop_column(
        'renewals',
        'assigned_to'
    )

    op.drop_column(
        'renewals',
        'new_expiry_date'
    )

    op.drop_column(
        'renewals',
        'previous_expiry_date'
    )