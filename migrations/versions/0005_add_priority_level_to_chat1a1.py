"""Add priority_level column to chat1a1_sessions

Revision ID: 0005_add_priority_level_to_chat1a1
Revises: 0004_add_triage_columns
Create Date: 2025-09-05 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0005_add_priority_level_to_chat1a1'
down_revision = '0004_add_triage_columns'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar coluna priority_level na tabela chat1a1_sessions se não existir
    with op.batch_alter_table('chat1a1_sessions') as batch_op:
        batch_op.add_column(sa.Column('priority_level', sa.String(length=20), nullable=False, server_default='normal'))


def downgrade():
    # Remover a coluna priority_level
    with op.batch_alter_table('chat1a1_sessions') as batch_op:
        batch_op.drop_column('priority_level')
