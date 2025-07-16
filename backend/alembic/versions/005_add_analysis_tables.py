"""Add analysis tables

Revision ID: 005
Revises: 004
Create Date: 2024-07-16 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    # Create analysis_tasks table
    op.create_table('analysis_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('transcription_task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('task_id', sa.String(length=100), nullable=False),
        sa.Column('analysis_type', sa.String(length=50), nullable=False),
        sa.Column('focus_areas', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('custom_prompts', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('progress', sa.Integer(), nullable=False),
        sa.Column('stage', sa.String(length=100), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('estimated_duration', sa.Integer(), nullable=True),
        sa.Column('actual_duration', sa.Integer(), nullable=True),
        sa.Column('estimated_completion', sa.DateTime(), nullable=True),
        sa.Column('full_analysis_result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('suggestions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('cost', sa.Float(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_code', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['transcription_task_id'], ['transcription_tasks.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_analysis_tasks_created_at', 'analysis_tasks', ['created_at'])
    op.create_index('ix_analysis_tasks_is_deleted', 'analysis_tasks', ['is_deleted'])
    op.create_index('ix_analysis_tasks_session_id', 'analysis_tasks', ['session_id'])
    op.create_index('ix_analysis_tasks_status', 'analysis_tasks', ['status'])
    op.create_index('ix_analysis_tasks_task_id', 'analysis_tasks', ['task_id'])
    op.create_index('ix_analysis_tasks_transcription_task_id', 'analysis_tasks', ['transcription_task_id'])

    # Create analysis_feedback table
    op.create_table('analysis_feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('analysis_task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('feedback_text', sa.Text(), nullable=True),
        sa.Column('category_ratings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('suggestions_helpful', sa.Boolean(), nullable=True),
        sa.Column('accuracy_rating', sa.Integer(), nullable=True),
        sa.Column('improvement_suggestions', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['analysis_task_id'], ['analysis_tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_analysis_feedback_analysis_task_id', 'analysis_feedback', ['analysis_task_id'])
    op.create_index('ix_analysis_feedback_created_at', 'analysis_feedback', ['created_at'])
    op.create_index('ix_analysis_feedback_is_deleted', 'analysis_feedback', ['is_deleted'])
    op.create_index('ix_analysis_feedback_rating', 'analysis_feedback', ['rating'])
    op.create_index('ix_analysis_feedback_user_id', 'analysis_feedback', ['user_id'])

    # Create success_patterns table
    op.create_table('success_patterns',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('clinic_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pattern_type', sa.String(length=100), nullable=False),
        sa.Column('pattern_name', sa.String(length=200), nullable=False),
        sa.Column('pattern_description', sa.Text(), nullable=False),
        sa.Column('success_criteria', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('example_sessions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('effectiveness_score', sa.Float(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['clinic_id'], ['clinics.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_success_patterns_clinic_id', 'success_patterns', ['clinic_id'])
    op.create_index('ix_success_patterns_created_at', 'success_patterns', ['created_at'])
    op.create_index('ix_success_patterns_is_active', 'success_patterns', ['is_active'])
    op.create_index('ix_success_patterns_is_deleted', 'success_patterns', ['is_deleted'])
    op.create_index('ix_success_patterns_pattern_type', 'success_patterns', ['pattern_type'])


def downgrade():
    op.drop_table('success_patterns')
    op.drop_table('analysis_feedback')
    op.drop_table('analysis_tasks')