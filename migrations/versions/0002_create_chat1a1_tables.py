
"""
create chat1a1 tables

Revision ID: 0002_create_chat1a1_tables
Revises: 0001_full_init
Create Date: 2025-09-04 16:20:00.000000
"""
from alembic import op
import sqlalchemy as sa

# Revisão e dependência
revision = '0002_create_chat1a1_tables'
down_revision = '0001_full_init'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'chat1a1_sessions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('volunteer_id', sa.Integer, sa.ForeignKey('volunteers.id'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='ACTIVE'),
        sa.Column('title', sa.String(200), nullable=True),
        sa.Column('message_count', sa.Integer, nullable=False, default=0)
    )
    op.create_table(
        'chat1a1_messages',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('session_id', sa.Integer, sa.ForeignKey('chat1a1_sessions.id'), nullable=False),
        sa.Column('sender_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('message_type', sa.String(20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )

def downgrade():
    op.drop_table('chat1a1_messages')
    op.drop_table('chat1a1_sessions')
