"""update notifications for sprint 12

Revision ID: 1fe4018e8808
Revises: a6a2ab85b9b4
Create Date: 2026-08-29 17:41:56.136322

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1fe4018e8808"
down_revision: Union[str, Sequence[str], None] = "a6a2ab85b9b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ---------------------------------------------------------
    # 1. Add new columns as nullable first
    # ---------------------------------------------------------

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
            "title",
            sa.String(length=255),
            nullable=True
        )
    )

    op.add_column(
        "notifications",
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=True
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
            "updated_at",
            sa.DateTime(),
            nullable=True
        )
    )

    # ---------------------------------------------------------
    # 2. Migrate existing notification data
    # ---------------------------------------------------------

    # Existing notification_type values are preserved.
    #
    # Generate a title from the existing notification type.
    op.execute(
        """
        UPDATE notifications
        SET title = notification_type
        WHERE title IS NULL
        """
    )

    # Convert old is_read values into Sprint 12 status.
    op.execute(
        """
        UPDATE notifications
        SET status =
            CASE
                WHEN is_read = TRUE THEN 'Read'
                ELSE 'Unread'
            END
        WHERE status IS NULL
        """
    )

    # Existing created_at becomes updated_at
    # for existing records.
    op.execute(
        """
        UPDATE notifications
        SET updated_at = created_at
        WHERE updated_at IS NULL
        """
    )

    # For already-read notifications, use created_at
    # as the historical read timestamp.
    op.execute(
        """
        UPDATE notifications
        SET read_at = created_at
        WHERE is_read = TRUE
          AND read_at IS NULL
        """
    )

    # Existing notifications are considered sent.
    op.execute(
        """
        UPDATE notifications
        SET sent_at = created_at
        WHERE sent_at IS NULL
        """
    )

    # ---------------------------------------------------------
    # 3. Make required Sprint 12 fields NOT NULL
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # 4. Add foreign keys
    # ---------------------------------------------------------

    op.create_foreign_key(
        "fk_notifications_obligation_id",
        "notifications",
        "obligations",
        ["obligation_id"],
        ["id"]
    )

    op.create_foreign_key(
        "fk_notifications_contract_id",
        "notifications",
        "contracts",
        ["contract_id"],
        ["id"]
    )

    # ---------------------------------------------------------
    # 5. Remove old notification fields
    # ---------------------------------------------------------

    op.drop_column(
        "notifications",
        "is_read"
    )

    op.drop_column(
        "notifications",
        "channel"
    )


def downgrade() -> None:
    """Downgrade schema."""

    # ---------------------------------------------------------
    # 1. Restore old notification fields
    # ---------------------------------------------------------

    op.add_column(
        "notifications",
        sa.Column(
            "channel",
            sa.String(length=30),
            nullable=True
        )
    )

    op.add_column(
        "notifications",
        sa.Column(
            "is_read",
            sa.Boolean(),
            nullable=True
        )
    )

    # ---------------------------------------------------------
    # 2. Restore old values
    # ---------------------------------------------------------

    op.execute(
        """
        UPDATE notifications
        SET channel = 'In-App'
        WHERE channel IS NULL
        """
    )

    op.execute(
        """
        UPDATE notifications
        SET is_read =
            CASE
                WHEN status = 'Read' THEN TRUE
                ELSE FALSE
            END
        WHERE is_read IS NULL
        """
    )

    # ---------------------------------------------------------
    # 3. Make restored columns NOT NULL
    # ---------------------------------------------------------

    op.alter_column(
        "notifications",
        "channel",
        existing_type=sa.String(length=30),
        nullable=False
    )

    op.alter_column(
        "notifications",
        "is_read",
        existing_type=sa.Boolean(),
        nullable=False
    )

    # ---------------------------------------------------------
    # 4. Remove foreign keys
    # ---------------------------------------------------------

    op.drop_constraint(
        "fk_notifications_contract_id",
        "notifications",
        type_="foreignkey"
    )

    op.drop_constraint(
        "fk_notifications_obligation_id",
        "notifications",
        type_="foreignkey"
    )

    # ---------------------------------------------------------
    # 5. Remove Sprint 12 columns
    # ---------------------------------------------------------

    op.drop_column(
        "notifications",
        "updated_at"
    )

    op.drop_column(
        "notifications",
        "read_at"
    )

    op.drop_column(
        "notifications",
        "sent_at"
    )

    op.drop_column(
        "notifications",
        "scheduled_at"
    )

    op.drop_column(
        "notifications",
        "status"
    )

    op.drop_column(
        "notifications",
        "title"
    )

    op.drop_column(
        "notifications",
        "obligation_id"
    )

    op.drop_column(
        "notifications",
        "contract_id"
    )