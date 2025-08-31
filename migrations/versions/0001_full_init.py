"""
Migration inicial consolidada: cria todas as tabelas e campos necessários do sistema, incluindo ajuste do alembic_version.
"""
from alembic import op
import sqlalchemy as sa

revision = '0001_full_init'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Ajusta o alembic_version
    with op.batch_alter_table('alembic_version') as batch_op:
        batch_op.alter_column('version_num',
            existing_type=sa.VARCHAR(length=32),
            type_=sa.VARCHAR(length=255),
            existing_nullable=False)

    # USERS
    op.create_table('users',
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=50), nullable=False),
        sa.Column('last_name', sa.String(length=50), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('role', sa.Enum('ADMIN', 'CLIENT', 'VOLUNTEER', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=True),
        sa.Column('locked_until', sa.DateTime(), nullable=True),
        sa.Column('terms_accepted', sa.Boolean(), nullable=False),
        sa.Column('terms_accepted_at', sa.DateTime(), nullable=True),
        sa.Column('privacy_policy_accepted', sa.Boolean(), nullable=False),
        sa.Column('privacy_policy_accepted_at', sa.DateTime(), nullable=True),
        sa.Column('data_processing_consent', sa.Boolean(), nullable=False),
        sa.Column('data_processing_consent_at', sa.DateTime(), nullable=True),
        sa.Column('is_anonymized', sa.Boolean(), nullable=False),
        sa.Column('anonymized_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # ADMIN_LOGS
    op.create_table('admin_logs',
        sa.Column('admin_user_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.Enum('USER_CREATED', 'USER_UPDATED', 'USER_DELETED', 'USER_ACTIVATED', 'USER_DEACTIVATED', 'USER_ROLE_CHANGED', 'VOLUNTEER_APPROVED', 'VOLUNTEER_REJECTED', 'VOLUNTEER_SUSPENDED', 'VOLUNTEER_REACTIVATED', 'CONTENT_MODERATED', 'CONTENT_REMOVED', 'CONTENT_FLAGGED', 'RISK_REVIEW', 'EMERGENCY_ESCALATION', 'MANUAL_INTERVENTION', 'SYSTEM_CONFIG_CHANGED', 'DATABASE_MAINTENANCE', 'DATA_EXPORT', 'DATA_ANONYMIZATION', 'AUDIT_PERFORMED', 'GDPR_REQUEST', 'DATA_BREACH_RESPONSE', 'LOGIN_ATTEMPT', 'PASSWORD_RESET', 'SECURITY_INCIDENT', name='adminaction'), nullable=False),
        sa.Column('level', sa.Enum('INFO', 'WARNING', 'ERROR', 'CRITICAL', name='loglevel'), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('target_user_id', sa.Integer(), nullable=True),
        sa.Column('target_type', sa.String(length=50), nullable=True),
        sa.Column('target_id', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('before_state', sa.Text(), nullable=True),
        sa.Column('after_state', sa.Text(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['admin_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['target_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # DIARY_ENTRIES
    op.create_table('diary_entries',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('mood_level', sa.Integer(), nullable=True),
        sa.Column('emotions', sa.Text(), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('risk_level', sa.String(length=20), nullable=True),
        sa.Column('risk_factors', sa.Text(), nullable=True),
        sa.Column('keywords', sa.Text(), nullable=True),
        sa.Column('is_private', sa.Boolean(), nullable=False),
        sa.Column('visible_to_volunteers', sa.Boolean(), nullable=False),
        sa.Column('word_count', sa.Integer(), nullable=True),
        sa.Column('reading_time_minutes', sa.Integer(), nullable=True),
        sa.Column('is_anonymized', sa.Boolean(), nullable=False),
        sa.Column('anonymized_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # VOLUNTEERS
    op.create_table('volunteers',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('profession', sa.String(length=100), nullable=True),
        sa.Column('specialization', sa.String(length=200), nullable=True),
        sa.Column('experience_years', sa.Integer(), nullable=True),
        sa.Column('education', sa.Text(), nullable=True),
        sa.Column('certifications', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'ACTIVE', 'INACTIVE', 'SUSPENDED', 'BLOCKED', name='volunteerstatus'), nullable=False),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('is_available', sa.Boolean(), nullable=False),
        sa.Column('max_concurrent_chats', sa.Integer(), nullable=False),
        sa.Column('current_active_chats', sa.Integer(), nullable=False),
        sa.Column('total_chats', sa.Integer(), nullable=False),
        sa.Column('total_hours', sa.Float(), nullable=False),
        sa.Column('average_rating', sa.Float(), nullable=True),
        sa.Column('total_ratings', sa.Integer(), nullable=False),
        sa.Column('auto_assign', sa.Boolean(), nullable=False),
        sa.Column('emergency_contact', sa.Boolean(), nullable=False),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('last_activity', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # CHAT_SESSIONS
    op.create_table('chat_sessions',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('volunteer_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'COMPLETED', 'ABANDONED', 'TRANSFERRED', name='chatsessionstatus'), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('initial_risk_level', sa.String(length=20), nullable=True),
        sa.Column('final_risk_level', sa.String(length=20), nullable=True),
        sa.Column('risk_factors', sa.Text(), nullable=True),
        sa.Column('user_rating', sa.Integer(), nullable=True),
        sa.Column('user_feedback', sa.Text(), nullable=True),
        sa.Column('volunteer_notes', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('message_count', sa.Integer(), nullable=True),
        sa.Column('is_anonymized', sa.Boolean(), nullable=False),
        sa.Column('anonymized_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['volunteer_id'], ['volunteers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # VOLUNTEER_AVAILABILITY
    op.create_table('volunteer_availability',
        sa.Column('volunteer_id', sa.Integer(), nullable=False),
        sa.Column('day_of_week', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('notes', sa.String(length=200), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['volunteer_id'], ['volunteers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('volunteer_id', 'day_of_week', name='unique_volunteer_day')
    )

    # VOLUNTEER_SKILLS
    op.create_table('volunteer_skills',
        sa.Column('volunteer_id', sa.Integer(), nullable=False),
        sa.Column('skill_name', sa.String(length=100), nullable=False),
        sa.Column('level', sa.Enum('BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT', name='skilllevel'), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('verified_by', sa.Integer(), nullable=True),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['verified_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['volunteer_id'], ['volunteers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('volunteer_id', 'skill_name', name='unique_volunteer_skill')
    )

    # CHAT_MESSAGES
    op.create_table('chat_messages',
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('message_type', sa.Enum('USER', 'AI', 'VOLUNTEER', 'SYSTEM', name='chatmessagetype'), nullable=False),
        sa.Column('message_metadata', sa.Text(), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('risk_indicators', sa.Text(), nullable=True),
        sa.Column('ai_model_used', sa.String(length=100), nullable=True),
        sa.Column('ai_confidence', sa.Float(), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('is_anonymized', sa.Boolean(), nullable=False),
        sa.Column('anonymized_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # TRIAGE_LOGS
    op.create_table('triage_logs',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('chat_session_id', sa.Integer(), nullable=True),
        sa.Column('diary_entry_id', sa.Integer(), nullable=True),
        sa.Column('risk_level', sa.Enum('LOW', 'MODERATE', 'HIGH', 'CRITICAL', name='risklevel'), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('risk_factors', sa.Text(), nullable=True),
        sa.Column('trigger_content', sa.Text(), nullable=True),
        sa.Column('context_type', sa.String(length=50), nullable=False),
        sa.Column('suicidal_ideation', sa.Boolean(), nullable=False),
        sa.Column('self_harm_risk', sa.Boolean(), nullable=False),
        sa.Column('substance_abuse', sa.Boolean(), nullable=False),
        sa.Column('domestic_violence', sa.Boolean(), nullable=False),
        sa.Column('severe_depression', sa.Boolean(), nullable=False),
        sa.Column('anxiety_disorder', sa.Boolean(), nullable=False),
        sa.Column('action_taken', sa.Enum('MONITORED', 'ESCALATED', 'EMERGENCY_CONTACT', 'PROFESSIONAL_REFERRAL', 'SELF_HELP_SUGGESTED', name='triageaction'), nullable=True),
        sa.Column('action_details', sa.Text(), nullable=True),
        sa.Column('follow_up_required', sa.Boolean(), nullable=False),
        sa.Column('follow_up_date', sa.DateTime(), nullable=True),
        sa.Column('analyzed_by_ai', sa.Boolean(), nullable=False),
        sa.Column('reviewed_by_human', sa.Boolean(), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('ai_model_used', sa.String(length=100), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('keywords_detected', sa.Text(), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('is_anonymized', sa.Boolean(), nullable=False),
        sa.Column('anonymized_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['chat_session_id'], ['chat_sessions.id'], ),
        sa.ForeignKeyConstraint(['diary_entry_id'], ['diary_entries.id'], ),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # TRAINING_DATA (com embedding vetorial)
    op.create_table('training_data',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('content', sa.Text, nullable=True),
        sa.Column('file_name', sa.String(255), nullable=True),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('file_size', sa.Integer, nullable=True),
        sa.Column('file_type', sa.String(50), nullable=True),
        sa.Column('data_type', sa.String(50), nullable=False, server_default='TEXT'),
        sa.Column('status', sa.String(50), nullable=False, server_default='PENDING'),
        sa.Column('validation_notes', sa.Text, nullable=True),
        sa.Column('validation_score', sa.Float, nullable=True),
        sa.Column('submitted_by', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('validated_by', sa.Integer, sa.ForeignKey('users.id'), nullable=True),
        sa.Column('validated_at', sa.DateTime, nullable=True),
        sa.Column('processed_at', sa.DateTime, nullable=True),
        sa.Column('processing_logs', sa.Text, nullable=True),
        sa.Column('embedding', sa.LargeBinary, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )

    # Índices e colunas extras
    op.add_column('chat_sessions', sa.Column('last_activity', sa.DateTime(), nullable=True))
    op.add_column('chat_sessions', sa.Column('uuid', sa.String(length=36), nullable=True, unique=True))
    op.create_index('idx_chat_sessions_user_status', 'chat_sessions', ['user_id', 'status'])
    op.create_index('idx_chat_sessions_last_activity', 'chat_sessions', ['last_activity'])
    op.create_index('idx_chat_sessions_status_last_activity', 'chat_sessions', ['status', 'last_activity'])
    op.create_index('idx_chat_sessions_uuid', 'chat_sessions', ['uuid'])
    op.create_index('idx_chat_messages_session_created', 'chat_messages', ['session_id', 'created_at'])
    op.create_index('idx_chat_messages_created_at', 'chat_messages', ['created_at'])
    op.create_index('idx_chat_messages_session_type', 'chat_messages', ['session_id', 'message_type'])

def downgrade():
    op.drop_index('idx_chat_messages_session_type', table_name='chat_messages')
    op.drop_index('idx_chat_messages_created_at', table_name='chat_messages')
    op.drop_index('idx_chat_messages_session_created', table_name='chat_messages')
    op.drop_index('idx_chat_sessions_uuid', table_name='chat_sessions')
    op.drop_index('idx_chat_sessions_status_last_activity', table_name='chat_sessions')
    op.drop_index('idx_chat_sessions_last_activity', table_name='chat_sessions')
    op.drop_index('idx_chat_sessions_user_status', table_name='chat_sessions')
    op.drop_column('chat_sessions', 'uuid')
    op.drop_column('chat_sessions', 'last_activity')
    op.drop_table('training_data')
    op.drop_table('triage_logs')
    op.drop_table('chat_messages')
    op.drop_table('volunteer_skills')
    op.drop_table('volunteer_availability')
    op.drop_table('chat_sessions')
    op.drop_table('volunteers')
    op.drop_table('diary_entries')
    op.drop_table('admin_logs')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    with op.batch_alter_table('alembic_version') as batch_op:
        batch_op.alter_column('version_num',
            existing_type=sa.VARCHAR(length=255),
            type_=sa.VARCHAR(length=32),
            existing_nullable=False)