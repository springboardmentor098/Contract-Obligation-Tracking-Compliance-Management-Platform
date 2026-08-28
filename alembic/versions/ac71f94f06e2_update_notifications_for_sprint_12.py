"""update notifications for sprint 12

Revision ID: ac71f94f06e2
Revises: bfe39eaf3231
Create Date: 2026-08-28

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# =========================================================
# REVISION IDENTIFIERS
# =========================================================

revision: str = "ac71f94f06e2"

down_revision: Union[str, Sequence[str], None] = "bfe39eaf3231"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


# =========================================================
# UPGRADE
# =========================================================

def upgrade() -> None:

    # -----------------------------------------------------
    # Add title
    # -----------------------------------------------------

    op.add_column(
        "notifications",
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=True,
        ),
    )

    # -----------------------------------------------------
    # Add status
    # -----------------------------------------------------

    op.add_column(
        "notifications",
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=True,
        ),
    )

    # -----------------------------------------------------
    # Add scheduled_at
    # -----------------------------------------------------

    op.add_column(
        "notifications",
        sa.Column(
            "scheduled_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    # -----------------------------------------------------
    # Add read_at
    # -----------------------------------------------------

    op.add_column(
        "notifications",
        sa.Column(
            "read_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    # -----------------------------------------------------
    # Add updated_at
    # -----------------------------------------------------

    op.add_column(
        "notifications",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    # -----------------------------------------------------
    # Populate title for existing notifications
    # -----------------------------------------------------

    op.execute(
        """
        UPDATE notifications
        SET title = notification_type
        WHERE title IS NULL
        """
    )

    # -----------------------------------------------------
    # Populate status using existing is_read column
    # -----------------------------------------------------

    op.execute(
        """
        UPDATE notifications
        SET status =
            CASE
                WHEN is_read = TRUE THEN 'Read'
                ELSE 'Unread'
            END
        """
    )

    # -----------------------------------------------------
    # Populate updated_at for existing records
    # -----------------------------------------------------

    op.execute(
        """
        UPDATE notifications
        SET updated_at = created_at
        WHERE updated_at IS NULL
        """
    )

    # -----------------------------------------------------
    # Make required columns NOT NULL
    # -----------------------------------------------------

    op.alter_column(
        "notifications",
        "title",
        existing_type=sa.String(length=255),
        nullable=False,
    )

    op.alter_column(
        "notifications",
        "status",
        existing_type=sa.String(length=20),
        nullable=False,
    )

    op.alter_column(
        "notifications",
        "updated_at",
        existing_type=sa.DateTime(),
        nullable=False,
    )

    # -----------------------------------------------------
    # Set default status for future notifications
    # -----------------------------------------------------

    op.alter_column(
        "notifications",
        "status",
        existing_type=sa.String(length=20),
        server_default="Unread",
    )

    # -----------------------------------------------------
    # Remove old channel column
    # -----------------------------------------------------

    op.drop_column(
        "notifications",
        "channel",
    )

    # -----------------------------------------------------
    # Remove old is_read column
    # -----------------------------------------------------

    op.drop_column(
        "notifications",
        "is_read",
    )


# =========================================================
# DOWNGRADE
# =========================================================

def downgrade() -> None:

    # -----------------------------------------------------
    # Restore is_read
    # -----------------------------------------------------

    op.add_column(
        "notifications",
        sa.Column(
            "is_read",
            sa.Boolean(),
            nullable=True,
        ),
    )

    # -----------------------------------------------------
    # Restore channel
    # -----------------------------------------------------

    op.add_column(
        "notifications",
        sa.Column(
            "channel",
            sa.String(length=50),
            nullable=True,
        ),
    )

    # -----------------------------------------------------
    # Restore is_read based on status
    # -----------------------------------------------------

    op.execute(
        """
        UPDATE notifications
        SET is_read =
            CASE
                WHEN status = 'Read' THEN TRUE
                ELSE FALSE
            END
        """
    )

    # -----------------------------------------------------
    # Set default channel for existing records
    # -----------------------------------------------------

    op.execute(
        """
        UPDATE notifications
        SET channel = 'In-App'
        WHERE channel IS NULL
        """
    )

    # -----------------------------------------------------
    # Make restored columns NOT NULL
    # -----------------------------------------------------

    op.alter_column(
        "notifications",
        "is_read",
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=sa.false(),
    )

    op.alter_column(
        "notifications",
        "channel",
        existing_type=sa.String(length=50),
        nullable=False,
    )

    # -----------------------------------------------------
    # Remove Sprint 12 columns
    # -----------------------------------------------------

    op.drop_column(
        "notifications",
        "updated_at",
    )

    op.drop_column(
        "notifications",
        "read_at",
    )

    op.drop_column(
        "notifications",
        "scheduled_at",
    )

    op.drop_column(
        "notifications",
        "status",
    )

    op.drop_column(
        "notifications",
        "title",
    )