"""implement ContractIQ database schema

Revision ID: a3b28be216a3
Revises: 600cf4ad0c60
Create Date: 2026-08-11 18:32:54.733537

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "a3b28be216a3"
down_revision: Union[str, Sequence[str], None] = "600cf4ad0c60"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ============================================================
    # 1. Convert existing users table from INTEGER ID to UUID
    # ============================================================

    op.add_column(
        "users",
        sa.Column(
            "new_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    op.execute(
        sa.text(
            "UPDATE users SET new_id = gen_random_uuid()"
        )
    )

    op.add_column(
        "users",
        sa.Column(
            "password_hash",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.execute(
        sa.text(
            "UPDATE users SET password_hash = password"
        )
    )

    op.add_column(
        "users",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    op.execute(
        sa.text(
            """
            UPDATE users
            SET created_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            """
        )
    )

    # Remove old primary key.
    op.drop_constraint(
        "users_pkey",
        "users",
        type_="primary",
    )

    # Remove old INTEGER id.
    op.drop_column("users", "id")

    # Rename UUID column to id.
    op.alter_column(
        "users",
        "new_id",
        new_column_name="id",
    )

    # UUID id must not be NULL.
    op.alter_column(
        "users",
        "id",
        nullable=False,
    )

    # Create new UUID primary key.
    op.create_primary_key(
        "users_pkey",
        "users",
        ["id"],
    )

    # Increase full_name length from 100 to 150.
    op.alter_column(
        "users",
        "full_name",
        existing_type=sa.String(length=100),
        type_=sa.String(length=150),
        existing_nullable=False,
    )

    # Remove old password column.
    op.drop_column(
        "users",
        "password",
    )

    # Make new fields required.
    op.alter_column(
        "users",
        "password_hash",
        nullable=False,
    )

    op.alter_column(
        "users",
        "created_at",
        nullable=False,
    )

    op.alter_column(
        "users",
        "updated_at",
        nullable=False,
    )

    # ============================================================
    # 2. Create contracts
    # ============================================================

    op.create_table(
        "contracts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "contract_number",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "owner_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "contract_type",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "counterparty_name",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "start_date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "end_date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "contract_value",
            sa.Numeric(15, 2),
            nullable=True,
        ),
        sa.Column(
            "currency",
            sa.CHAR(3),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ============================================================
    # 3. Create contract_versions
    # ============================================================

    op.create_table(
        "contract_versions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "contract_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "version_number",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "version_label",
            sa.String(50),
            nullable=True,
        ),
        sa.Column(
            "file_name",
            sa.String(255),
            nullable=True,
        ),
        sa.Column(
            "file_path",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "change_summary",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["contract_id"],
            ["contracts.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ============================================================
    # 4. Create obligations
    # ============================================================

    op.create_table(
        "obligations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "contract_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "assigned_to",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "obligation_type",
            sa.String(100),
            nullable=True,
        ),
        sa.Column(
            "due_date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(50),
            nullable=True,
        ),
        sa.Column(
            "priority",
            sa.String(20),
            nullable=True,
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["contract_id"],
            ["contracts.id"],
        ),
        sa.ForeignKeyConstraint(
            ["assigned_to"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ============================================================
    # 5. Create renewals
    # ============================================================

    op.create_table(
        "renewals",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "contract_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "initiated_by",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "previous_end_date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "renewal_date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "new_end_date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(50),
            nullable=True,
        ),
        sa.Column(
            "notes",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["contract_id"],
            ["contracts.id"],
        ),
        sa.ForeignKeyConstraint(
            ["initiated_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ============================================================
    # 6. Create notifications
    # ============================================================

    op.create_table(
        "notifications",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "contract_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "obligation_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "notification_type",
            sa.String(50),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "message",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "scheduled_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "sent_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "read_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(30),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["contract_id"],
            ["contracts.id"],
        ),
        sa.ForeignKeyConstraint(
            ["obligation_id"],
            ["obligations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ============================================================
    # 7. Create reports
    # ============================================================

    op.create_table(
        "reports",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "contract_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "generated_by",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "report_type",
            sa.String(100),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "parameters",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "file_path",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "generated_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["contract_id"],
            ["contracts.id"],
        ),
        sa.ForeignKeyConstraint(
            ["generated_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ============================================================
    # 8. Create audit_logs
    # ============================================================

    op.create_table(
        "audit_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "entity_type",
            sa.String(100),
            nullable=False,
        ),
        sa.Column(
            "entity_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "action",
            sa.String(50),
            nullable=False,
        ),
        sa.Column(
            "old_values",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "new_values",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "ip_address",
            sa.String(45),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ============================================================
    # 9. Create activities
    # ============================================================

    op.create_table(
        "activities",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "contract_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "obligation_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "activity_type",
            sa.String(100),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["contract_id"],
            ["contracts.id"],
        ),
        sa.ForeignKeyConstraint(
            ["obligation_id"],
            ["obligations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_table("activities")
    op.drop_table("audit_logs")
    op.drop_table("reports")
    op.drop_table("notifications")
    op.drop_table("renewals")
    op.drop_table("obligations")
    op.drop_table("contract_versions")
    op.drop_table("contracts")

    # The UUID user IDs cannot generically be converted back
    # to their original INTEGER values.
    # This downgrade is therefore intentionally limited.

    op.drop_column("users", "password_hash")
    op.drop_column("users", "created_at")
    op.drop_column("users", "updated_at")