"""preserve audit logs when contracts are deleted

Revision ID: 5fa9995e6849
Revises: dd5e169a9f88
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "5fa9995e6849"
down_revision: Union[str, Sequence[str], None] = "dd5e169a9f88"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "audit_logs_contract_id_fkey",
        "audit_logs",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "audit_logs_contract_id_fkey",
        "audit_logs",
        "contracts",
        ["contract_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "audit_logs_contract_id_fkey",
        "audit_logs",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "audit_logs_contract_id_fkey",
        "audit_logs",
        "contracts",
        ["contract_id"],
        ["id"],
        ondelete="CASCADE",
    )
