"""upgrade compliance monitoring and history

Revision ID: 3ac81abe1ba5
Revises: cc61257b58e5
Create Date: 2026-08-31
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "3ac81abe1ba5"
down_revision: Union[str, Sequence[str], None] = "cc61257b58e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # Add contract_id
    op.add_column(
        "compliances",
        sa.Column(
            "contract_id",
            sa.Integer(),
            nullable=True
        )
    )

    # Add compliance_score
    op.add_column(
        "compliances",
        sa.Column(
            "compliance_score",
            sa.Float(),
            nullable=True
        )
    )

    # Add risk_level
    op.add_column(
        "compliances",
        sa.Column(
            "risk_level",
            sa.String(length=50),
            nullable=True
        )
    )

    # Add evaluated_at
    op.add_column(
        "compliances",
        sa.Column(
            "evaluated_at",
            sa.DateTime(),
            nullable=True
        )
    )

    # Add notes
    op.add_column(
        "compliances",
        sa.Column(
            "notes",
            sa.Text(),
            nullable=True
        )
    )

    # Add created_at
    op.add_column(
        "compliances",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True
        )
    )

    # Add updated_at
    op.add_column(
        "compliances",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True
        )
    )

    # Foreign key for contract
    op.create_foreign_key(
        "compliances_contract_id_fkey",
        "compliances",
        "contracts",
        ["contract_id"],
        ["id"]
    )


def downgrade() -> None:

    op.drop_constraint(
        "compliances_contract_id_fkey",
        "compliances",
        type_="foreignkey"
    )

    op.drop_column("compliances", "updated_at")
    op.drop_column("compliances", "created_at")
    op.drop_column("compliances", "notes")
    op.drop_column("compliances", "evaluated_at")
    op.drop_column("compliances", "risk_level")
    op.drop_column("compliances", "compliance_score")
    op.drop_column("compliances", "contract_id")