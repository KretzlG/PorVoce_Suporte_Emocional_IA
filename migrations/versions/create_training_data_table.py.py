"""Cria a tabela training_data"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'a1_create_training_data_table'
down_revision = 'fec4fa3d6b59'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'training_data',
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
        sa.Column('processing_logs', sa.Text, nullable=True)
    )

def downgrade():
    op.drop_table('training_data')
