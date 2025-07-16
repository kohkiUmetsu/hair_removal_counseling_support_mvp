"""Add transcription_tasks table

Revision ID: 004
Revises: 003
Create Date: 2025-07-16 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create transcription_tasks table
    op.create_table('transcription_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recording_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('task_id', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='pending', nullable=False),
        sa.Column('progress', sa.Integer(), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('temperature', sa.Float(), nullable=False),
        sa.Column('transcription_text', sa.Text(), nullable=True),
        sa.Column('transcription_result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('detected_language', sa.String(length=10), nullable=True),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_code', sa.String(length=50), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('estimated_completion', sa.DateTime(), nullable=True),
        sa.Column('estimated_duration', sa.Integer(), nullable=True),
        sa.Column('actual_duration', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['recording_id'], ['recordings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_transcription_tasks_id', 'transcription_tasks', ['id'], unique=False)
    op.create_index('ix_transcription_tasks_recording_id', 'transcription_tasks', ['recording_id'], unique=False)
    op.create_index('ix_transcription_tasks_session_id', 'transcription_tasks', ['session_id'], unique=False)
    op.create_index('ix_transcription_tasks_task_id', 'transcription_tasks', ['task_id'], unique=True)
    op.create_index('ix_transcription_tasks_status', 'transcription_tasks', ['status'], unique=False)
    op.create_index('ix_transcription_tasks_created_at', 'transcription_tasks', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_transcription_tasks_created_at', table_name='transcription_tasks')
    op.drop_index('ix_transcription_tasks_status', table_name='transcription_tasks')
    op.drop_index('ix_transcription_tasks_task_id', table_name='transcription_tasks')
    op.drop_index('ix_transcription_tasks_session_id', table_name='transcription_tasks')
    op.drop_index('ix_transcription_tasks_recording_id', table_name='transcription_tasks')
    op.drop_index('ix_transcription_tasks_id', table_name='transcription_tasks')
    
    # Drop table
    op.drop_table('transcription_tasks')