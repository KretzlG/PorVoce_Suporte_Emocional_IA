"""Fix volunteer_id nullable constraint in chat1a1_sessions

Revision ID: 0006_fix_volunteer_id_nullable
Revises: 0005_add_priority_level_to_chat1a1
Create Date: 2025-09-05 19:25:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0006_fix_volunteer_id_nullable'
down_revision = '0005_add_priority_level_to_chat1a1'
branch_labels = None
depends_on = None


def upgrade():
    # Alterar coluna volunteer_id para permitir NULL
    with op.batch_alter_table('chat1a1_sessions', schema=None) as batch_op:
        batch_op.alter_column('volunteer_id', nullable=True)


def downgrade():
    # Voltar a coluna volunteer_id para NOT NULL (se necessário)
    with op.batch_alter_table('chat1a1_sessions', schema=None) as batch_op:
        batch_op.alter_column('volunteer_id', nullable=False)
