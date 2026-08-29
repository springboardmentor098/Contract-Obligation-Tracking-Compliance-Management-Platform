"""create notifications table

Revision ID: 3ded42e615d9
Revises: 8847f0c2f3fc
Create Date: 2026-08-28 23:11:11.516236
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "3ded42e615d9"
down_revision: Union[str, Sequence[str], None] = "8847f0c2f3fc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add new notification columns.
    # server_default is used because existing rows already exist.

    op.add_column(
        "notifications",
        sa.Column(
            "contract_id",
            sa.Integer(),
            nullable=True
        )
    )

    op.add_column(
        "notifications",
        sa.Column(
            "obligation_id",
            sa.Integer(),
            nullable=True
        )
    )

    op.add_column(
        "notifications",
        sa.Column(
            "notification_type",
            sa.String(length=100),
            nullable=False,
            server_default="General"
        )
    )

    op.add_column(
        "notifications",
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
            server_default="Notification"
        )
    )

    op.add_column(
        "notifications",
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="Unread"
        )
    )

    op.add_column(
        "notifications",
        sa.Column(
            "scheduled_at",
            sa.DateTime(),
            nullable=True
        )
    )

    op.add_column(
        "notifications",
        sa.Column(
            "sent_at",
            sa.DateTime(),
            nullable=True
        )
    )

    op.add_column(
        "notifications",
        sa.Column(
            "read_at",
            sa.DateTime(),
            nullable=True
        )
    )

    op.add_column(
        "notifications",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now()
        )
    )

    op.add_column(
        "notifications",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now()
        )
    )

    # Foreign keys
    op.create_foreign_key(
        None,
        "notifications",
        "contracts",
        ["contract_id"],
        ["id"]
    )

    op.create_foreign_key(
        None,
        "notifications",
        "obligations",
        ["obligation_id"],
        ["id"]
    )

    # Remove old column
    op.drop_column(
        "notifications",
        "is_read"
    )

    # Renewals changes
    op.alter_column(
        "renewals",
        "previous_expiry_date",
        existing_type=sa.DATE(),
        nullable=False
    )

    op.alter_column(
        "renewals",
        "new_expiry_date",
        existing_type=sa.DATE(),
        nullable=False
    )

    op.alter_column(
        "renewals",
        "assigned_to",
        existing_type=sa.INTEGER(),
        nullable=False
    )

    op.alter_column(
        "renewals",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False
    )

    op.alter_column(
        "renewals",
        "updated_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Renewals changes
    op.alter_column(
        "renewals",
        "updated_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True
    )

    op.alter_column(
        "renewals",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True
    )

    op.alter_column(
        "renewals",
        "assigned_to",
        existing_type=sa.INTEGER(),
        nullable=True
    )

    op.alter_column(
        "renewals",
        "new_expiry_date",
        existing_type=sa.DATE(),
        nullable=True
    )

    op.alter_column(
        "renewals",
        "previous_expiry_date",
        existing_type=sa.DATE(),
        nullable=True
    )

    # Restore old column
    op.add_column(
        "notifications",
        sa.Column(
            "is_read",
            sa.BOOLEAN(),
            autoincrement=False,
            nullable=True
        )
    )

    # Remove foreign keys
    op.drop_constraint(
        None,
        "notifications",
        type_="foreignkey"
    )

    op.drop_constraint(
        None,
        "notifications",
        type_="foreignkey"
    )

    # Remove new columns
    op.drop_column("notifications", "updated_at")
    op.drop_column("notifications", "created_at")
    op.drop_column("notifications", "read_at")
    op.drop_column("notifications", "sent_at")
    op.drop_column("notifications", "scheduled_at")
    op.drop_column("notifications", "status")
    op.drop_column("notifications", "title")
    op.drop_column("notifications", "notification_type")
    op.drop_column("notifications", "obligation_id")
    op.drop_column("notifications", "contract_id")