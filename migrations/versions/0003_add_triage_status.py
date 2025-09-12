"""Add triage_status column to triage_logs

Revision ID: 0003_add_triage_status
Revises: 0002_create_chat1a1_tables
Create Date: 2025-09-05 10:50:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0003_add_triage_status'
down_revision = '0002_create_chat1a1_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar apenas a coluna triage_status à tabela triage_logs
    with op.batch_alter_table('triage_logs') as batch_op:
        batch_op.add_column(sa.Column('triage_status', sa.String(length=20), nullable=False, server_default='in_progress'))


def downgrade():
    # Remover a coluna triage_status da tabela triage_logs
    with op.batch_alter_table('triage_logs') as batch_op:
        batch_op.drop_column('triage_status')
