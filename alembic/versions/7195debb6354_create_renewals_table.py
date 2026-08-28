"""create renewals table

Revision ID: 7195debb6354
Revises: b1705af44707
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7195debb6354"
down_revision: Union[str, Sequence[str], None] = "b1705af44707"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns as nullable first
    op.add_column(
        "renewals",
        sa.Column(
            "previous_expiry_date",
            sa.Date(),
            nullable=True
        )
    )

    op.add_column(
        "renewals",
        sa.Column(
            "new_expiry_date",
            sa.Date(),
            nullable=True
        )
    )

    op.add_column(
        "renewals",
        sa.Column(
            "assigned_to",
            sa.Integer(),
            nullable=True
        )
    )

    op.add_column(
        "renewals",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=True
        )
    )

    op.add_column(
        "renewals",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True
        )
    )

    # Populate previous expiry date from the related contract
    op.execute(
        """
        UPDATE renewals r
        SET previous_expiry_date = c.end_date
        FROM contracts c
        WHERE r.contract_id = c.id
        """
    )

    # Populate timestamps for existing renewal records
    op.execute(
        """
        UPDATE renewals
        SET
            created_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE created_at IS NULL
           OR updated_at IS NULL
        """
    )

    # Make required fields NOT NULL after existing records are populated
    op.alter_column(
        "renewals",
        "previous_expiry_date",
        existing_type=sa.Date(),
        nullable=False
    )

    op.alter_column(
        "renewals",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False
    )

    op.alter_column(
        "renewals",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False
    )

    # Match the updated SQLAlchemy model
    op.alter_column(
        "renewals",
        "renewal_date",
        existing_type=sa.DATE(),
        nullable=True
    )

    # Foreign key for assigned user
    op.create_foreign_key(
        "fk_renewals_assigned_to_users",
        "renewals",
        "users",
        ["assigned_to"],
        ["id"]
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_renewals_assigned_to_users",
        "renewals",
        type_="foreignkey"
    )

    op.alter_column(
        "renewals",
        "renewal_date",
        existing_type=sa.DATE(),
        nullable=False
    )

    op.drop_column("renewals", "updated_at")
    op.drop_column("renewals", "created_at")
    op.drop_column("renewals", "assigned_to")
    op.drop_column("renewals", "new_expiry_date")
    op.drop_column("renewals", "previous_expiry_date")