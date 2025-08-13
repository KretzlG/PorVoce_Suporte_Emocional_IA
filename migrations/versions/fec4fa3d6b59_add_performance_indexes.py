"""add_performance_indexes

Revision ID: fec4fa3d6b59
Revises: 789102f483f3
Create Date: 2025-08-12 20:26:26.360480

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fec4fa3d6b59'
down_revision = '789102f483f3'
branch_labels = None
depends_on = None


def upgrade():
    # Índices críticos para ChatSession
    op.create_index('idx_chat_sessions_user_status', 'chat_sessions', ['user_id', 'status'])
    op.create_index('idx_chat_sessions_last_activity', 'chat_sessions', ['last_activity'])
    op.create_index('idx_chat_sessions_status_last_activity', 'chat_sessions', ['status', 'last_activity'])
    op.create_index('idx_chat_sessions_uuid', 'chat_sessions', ['uuid'])
    
    # Índices críticos para ChatMessage
    op.create_index('idx_chat_messages_session_created', 'chat_messages', ['session_id', 'created_at'])
    op.create_index('idx_chat_messages_created_at', 'chat_messages', ['created_at'])
    op.create_index('idx_chat_messages_session_type', 'chat_messages', ['session_id', 'message_type'])


def downgrade():
    # Remover índices
    op.drop_index('idx_chat_messages_session_type', table_name='chat_messages')
    op.drop_index('idx_chat_messages_created_at', table_name='chat_messages')
    op.drop_index('idx_chat_messages_session_created', table_name='chat_messages')
    op.drop_index('idx_chat_sessions_uuid', table_name='chat_sessions')
    op.drop_index('idx_chat_sessions_status_last_activity', table_name='chat_sessions')
    op.drop_index('idx_chat_sessions_last_activity', table_name='chat_sessions')
    op.drop_index('idx_chat_sessions_user_status', table_name='chat_sessions')
