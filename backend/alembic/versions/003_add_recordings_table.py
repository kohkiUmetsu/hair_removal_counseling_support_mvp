"""Add recordings table

Revision ID: 003
Revises: 002
Create Date: 2025-07-16 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create recordings table
    op.create_table('recordings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=True),
        sa.Column('content_type', sa.String(length=100), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('upload_status', sa.String(length=20), server_default='pending', nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_recordings_id', 'recordings', ['id'], unique=False)
    op.create_index('ix_recordings_customer_id', 'recordings', ['customer_id'], unique=False)
    op.create_index('ix_recordings_session_id', 'recordings', ['session_id'], unique=False)
    op.create_index('ix_recordings_file_path', 'recordings', ['file_path'], unique=True)
    op.create_index('ix_recordings_upload_status', 'recordings', ['upload_status'], unique=False)
    op.create_index('ix_recordings_created_at', 'recordings', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_recordings_created_at', table_name='recordings')
    op.drop_index('ix_recordings_upload_status', table_name='recordings')
    op.drop_index('ix_recordings_file_path', table_name='recordings')
    op.drop_index('ix_recordings_session_id', table_name='recordings')
    op.drop_index('ix_recordings_customer_id', table_name='recordings')
    op.drop_index('ix_recordings_id', table_name='recordings')
    
    # Drop table
    op.drop_table('recordings')