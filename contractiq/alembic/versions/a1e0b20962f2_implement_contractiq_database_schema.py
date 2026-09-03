"""implement ContractIQ database schema

Revision ID: a1e0b20962f2
Revises: 8dc50faf6b3c
Create Date: 2026-08-12 16:35:52.774320

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1e0b20962f2'
down_revision: Union[str, Sequence[str], None] = '8dc50faf6b3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""

    # Update existing users table first

    op.add_column(
        'users',
        sa.Column('password_hash', sa.String(length=255), nullable=True)
    )

    # Preserve existing password hashes
    op.execute(
        "UPDATE users SET password_hash = password"
    )

    # Make password_hash mandatory
    op.alter_column(
        'users',
        'password_hash',
        nullable=False
    )

    op.add_column(
        'users',
        sa.Column(
            'created_at',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=False
        )
    )

    op.add_column(
        'users',
        sa.Column(
            'updated_at',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=False
        )
    )

    op.alter_column(
        'users',
        'id',
        existing_type=sa.INTEGER(),
        type_=sa.BigInteger(),
        existing_nullable=False,
        autoincrement=True
    )

    op.alter_column(
        'users',
        'role',
        existing_type=sa.VARCHAR(length=50),
        type_=sa.String(length=40),
        existing_nullable=False
    )

    # Remove old password column
    op.drop_column('users', 'password')

    # --------------------------------------------------
    # CONTRACTS
    # --------------------------------------------------

    op.create_table(
        'contracts',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('owner_id', sa.BigInteger(), nullable=False),
        sa.Column('contract_code', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('counterparty', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('risk_level', sa.String(length=50), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_contracts_contract_code'),
        'contracts',
        ['contract_code'],
        unique=True
    )

    op.create_index(
        op.f('ix_contracts_id'),
        'contracts',
        ['id'],
        unique=False
    )

    # --------------------------------------------------
    # AUDIT LOGS
    # --------------------------------------------------

    op.create_table(
        'audit_logs',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('contract_id', sa.BigInteger(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_name', sa.String(length=100), nullable=False),
        sa.Column('entity_id', sa.BigInteger(), nullable=False),
        sa.Column('before_data', sa.Text(), nullable=True),
        sa.Column('after_data', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_audit_logs_id'),
        'audit_logs',
        ['id'],
        unique=False
    )

    # --------------------------------------------------
    # CONTRACT VERSIONS
    # --------------------------------------------------

    op.create_table(
        'contract_versions',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('contract_id', sa.BigInteger(), nullable=False),
        sa.Column('version_no', sa.Integer(), nullable=False),
        sa.Column('document_name', sa.String(length=255), nullable=False),
        sa.Column('document_uri', sa.Text(), nullable=False),
        sa.Column('checksum', sa.String(length=128), nullable=False),
        sa.Column('change_note', sa.Text(), nullable=True),
        sa.Column('uploaded_by', sa.BigInteger(), nullable=False),
        sa.Column(
            'uploaded_at',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id']),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_contract_versions_id'),
        'contract_versions',
        ['id'],
        unique=False
    )

    # --------------------------------------------------
    # OBLIGATIONS
    # --------------------------------------------------

    op.create_table(
        'obligations',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('contract_id', sa.BigInteger(), nullable=False),
        sa.Column('assigned_to', sa.BigInteger(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('frequency', sa.String(length=50), nullable=True),
        sa.Column('priority', sa.String(length=30), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('evidence_required', sa.Boolean(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id']),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_obligations_id'),
        'obligations',
        ['id'],
        unique=False
    )

    # --------------------------------------------------
    # RENEWALS
    # --------------------------------------------------

    op.create_table(
        'renewals',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('contract_id', sa.BigInteger(), nullable=False),
        sa.Column('managed_by', sa.BigInteger(), nullable=False),
        sa.Column('renewal_date', sa.Date(), nullable=False),
        sa.Column('notice_days', sa.Integer(), nullable=False),
        sa.Column('decision', sa.String(length=30), nullable=False),
        sa.Column('new_end_date', sa.Date(), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id']),
        sa.ForeignKeyConstraint(['managed_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_renewals_id'),
        'renewals',
        ['id'],
        unique=False
    )

    # --------------------------------------------------
    # REPORTS
    # --------------------------------------------------

    op.create_table(
        'reports',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('generated_by', sa.BigInteger(), nullable=False),
        sa.Column('contract_id', sa.BigInteger(), nullable=True),
        sa.Column('report_type', sa.String(length=50), nullable=False),
        sa.Column('report_name', sa.String(length=255), nullable=False),
        sa.Column('filters', sa.Text(), nullable=True),
        sa.Column('file_location', sa.Text(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id']),
        sa.ForeignKeyConstraint(['generated_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_reports_id'),
        'reports',
        ['id'],
        unique=False
    )

    # --------------------------------------------------
    # ACTIVITIES
    # --------------------------------------------------

    op.create_table(
        'activities',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('contract_id', sa.BigInteger(), nullable=True),
        sa.Column('obligation_id', sa.BigInteger(), nullable=True),
        sa.Column('activity_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id']),
        sa.ForeignKeyConstraint(['obligation_id'], ['obligations.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_activities_id'),
        'activities',
        ['id'],
        unique=False
    )

    # --------------------------------------------------
    # NOTIFICATIONS
    # --------------------------------------------------

    op.create_table(
        'notifications',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('contract_id', sa.BigInteger(), nullable=False),
        sa.Column('obligation_id', sa.BigInteger(), nullable=True),
        sa.Column('renewal_id', sa.BigInteger(), nullable=True),
        sa.Column('notification_type', sa.String(length=50), nullable=False),
        sa.Column('subject', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id']),
        sa.ForeignKeyConstraint(['obligation_id'], ['obligations.id']),
        sa.ForeignKeyConstraint(['renewal_id'], ['renewals.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_notifications_id'),
        'notifications',
        ['id'],
        unique=False
    )

    # ### end Alembic commands ###

def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('password', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
    op.alter_column('users', 'role',
               existing_type=sa.String(length=40),
               type_=sa.VARCHAR(length=50),
               existing_nullable=False)
    op.alter_column('users', 'id',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=False,
               autoincrement=True)
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'password_hash')
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_table('notifications')
    op.drop_index(op.f('ix_activities_id'), table_name='activities')
    op.drop_table('activities')
    op.drop_index(op.f('ix_reports_id'), table_name='reports')
    op.drop_table('reports')
    op.drop_index(op.f('ix_renewals_id'), table_name='renewals')
    op.drop_table('renewals')
    op.drop_index(op.f('ix_obligations_id'), table_name='obligations')
    op.drop_table('obligations')
    op.drop_index(op.f('ix_contract_versions_id'), table_name='contract_versions')
    op.drop_table('contract_versions')
    op.drop_index(op.f('ix_audit_logs_id'), table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_index(op.f('ix_contracts_id'), table_name='contracts')
    op.drop_index(op.f('ix_contracts_contract_code'), table_name='contracts')
    op.drop_table('contracts')
    # ### end Alembic commands ###
