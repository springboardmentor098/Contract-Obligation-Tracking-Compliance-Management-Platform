"""upgrade notifications for sprint 12

Revision ID: 35de24207694
Revises: 7195debb6354
Create Date: 2026-08-30 17:53:25.207769

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "35de24207694"
down_revision: Union[str, Sequence[str], None] = "7195debb6354"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns as nullable first
    op.add_column(
        "notifications",
        sa.Column("obligation_id", sa.Integer(), nullable=True)
    )

    op.add_column(
        "notifications",
        sa.Column("title", sa.String(length=255), nullable=True)
    )

    op.add_column(
        "notifications",
        sa.Column("status", sa.String(length=20), nullable=True)
    )

    op.add_column(
        "notifications",
        sa.Column("scheduled_at", sa.DateTime(), nullable=True)
    )

    op.add_column(
        "notifications",
        sa.Column("sent_at", sa.DateTime(), nullable=True)
    )

    op.add_column(
        "notifications",
        sa.Column("read_at", sa.DateTime(), nullable=True)
    )

    op.add_column(
        "notifications",
        sa.Column("updated_at", sa.DateTime(), nullable=True)
    )

    # Existing contract_id can be optional
    op.alter_column(
        "notifications",
        "contract_id",
        existing_type=sa.INTEGER(),
        nullable=True
    )

    # Populate new columns for existing records
    op.execute(
        """
        UPDATE notifications
        SET
            title = 'Notification',
            status = CASE
                WHEN is_read = TRUE THEN 'Read'
                ELSE 'Unread'
            END,
            updated_at = created_at
        WHERE title IS NULL
        """
    )

    # Add foreign key for obligation_id
    op.create_foreign_key(
        "fk_notifications_obligation_id",
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

    # Make required columns non-null
    op.alter_column(
        "notifications",
        "title",
        existing_type=sa.String(length=255),
        nullable=False
    )

    op.alter_column(
        "notifications",
        "status",
        existing_type=sa.String(length=20),
        nullable=False
    )

    op.alter_column(
        "notifications",
        "updated_at",
        existing_type=sa.DateTime(),
        nullable=False
    )


def downgrade() -> None:
    # Restore old is_read column
    op.add_column(
        "notifications",
        sa.Column(
            "is_read",
            sa.BOOLEAN(),
            nullable=False,
            server_default=sa.text("false")
        )
    )

    # Restore is_read based on status
    op.execute(
        """
        UPDATE notifications
        SET is_read = CASE
            WHEN status = 'Read' THEN TRUE
            ELSE FALSE
        END
        """
    )

    op.drop_constraint(
        "fk_notifications_obligation_id",
        "notifications",
        type_="foreignkey"
    )

    op.alter_column(
        "notifications",
        "contract_id",
        existing_type=sa.INTEGER(),
        nullable=False
    )

    op.drop_column("notifications", "updated_at")
    op.drop_column("notifications", "read_at")
    op.drop_column("notifications", "sent_at")
    op.drop_column("notifications", "scheduled_at")
    op.drop_column("notifications", "status")
    op.drop_column("notifications", "title")
    op.drop_column("notifications", "obligation_id")

    op.alter_column(
        "notifications",
        "is_read",
        server_default=None
    )