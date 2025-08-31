"""Adiciona coluna de embedding vetorial à tabela training_data para RAG"""

from alembic import op
import sqlalchemy as sa
import pgvector.sqlalchemy

# Revisão gerada pelo Alembic
revision = 'a2_add_training_embedding_vector'
down_revision = 'a1_create_training_data_table'
branch_labels = None
depends_on = None

def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    op.add_column('training_data', sa.Column('embedding', pgvector.sqlalchemy.Vector(1536), nullable=True, index=True, comment='Embedding para busca vetorial (RAG)'))

def downgrade():
    op.drop_column('training_data', 'embedding')
