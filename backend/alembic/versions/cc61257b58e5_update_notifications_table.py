"""update notifications table

Revision ID: cc61257b58e5
Revises: c6a458eaa826
Create Date: 2026-08-29 12:56:09.268031

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "cc61257b58e5"
down_revision: Union[str, Sequence[str], None] = "c6a458eaa826"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add obligation reference
    op.add_column(
        "notifications",
        sa.Column(
            "obligation_id",
            sa.Integer(),
            nullable=True
        )
    )

    # Add notification type
    op.add_column(
        "notifications",
        sa.Column(
            "notification_type",
            sa.String(length=100),
            nullable=True
        )
    )

    # Add notification title
    op.add_column(
        "notifications",
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=True
        )
    )

    # Add scheduling fields
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

    # Add read timestamp
    op.add_column(
        "notifications",
        sa.Column(
            "read_at",
            sa.DateTime(),
            nullable=True
        )
    )

    # Add timestamps
    op.add_column(
        "notifications",
        sa.Column(
            "created_at",
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

    # Allow contract_id to be optional
    op.alter_column(
        "notifications",
        "contract_id",
        existing_type=sa.INTEGER(),
        nullable=True
    )

    # Change message to Text and make it required
    op.alter_column(
        "notifications",
        "message",
        existing_type=sa.VARCHAR(length=500),
        type_=sa.Text(),
        nullable=False
    )

    # Foreign key for obligation
    op.create_foreign_key(
        "notifications_obligation_id_fkey",
        "notifications",
        "obligations",
        ["obligation_id"],
        ["id"]
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "notifications_obligation_id_fkey",
        "notifications",
        type_="foreignkey"
    )

    op.alter_column(
        "notifications",
        "message",
        existing_type=sa.Text(),
        type_=sa.VARCHAR(length=500),
        nullable=True
    )

    op.alter_column(
        "notifications",
        "contract_id",
        existing_type=sa.INTEGER(),
        nullable=False
    )

    op.drop_column("notifications", "updated_at")
    op.drop_column("notifications", "created_at")
    op.drop_column("notifications", "read_at")
    op.drop_column("notifications", "sent_at")
    op.drop_column("notifications", "scheduled_at")
    op.drop_column("notifications", "title")
    op.drop_column("notifications", "notification_type")
    op.drop_column("notifications", "obligation_id")