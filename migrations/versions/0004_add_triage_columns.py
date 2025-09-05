"""Add missing columns to triage_logs table

Revision ID: 0004_add_triage_columns
Revises: 0003_add_triage_status
Create Date: 2025-09-05 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0004_add_triage_columns'
down_revision = '0003_add_triage_status'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar colunas missing na tabela triage_logs
    with op.batch_alter_table('triage_logs') as batch_op:
        batch_op.add_column(sa.Column('emotional_state', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('notes', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('volunteer_assigned', sa.Integer(), nullable=True))


def downgrade():
    # Remover as colunas adicionadas
    with op.batch_alter_table('triage_logs') as batch_op:
        batch_op.drop_column('volunteer_assigned')
        batch_op.drop_column('notes')
        batch_op.drop_column('emotional_state')
