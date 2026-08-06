"""Remove unused diagnostico fields

Revision ID: 004
Revises: 003
Create Date: 2024-01-30 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('diagnostico', 'panaram_brief')
    op.drop_column('diagnostico', 'dores_identificadas')
    op.drop_column('diagnostico', 'solucao_proposta')
    op.drop_column('diagnostico', 'validacao_bant')


def downgrade() -> None:
    op.add_column('diagnostico', op.Column('panaram_brief', sa.Text(), nullable=True))
    op.add_column('diagnostico', op.Column('dores_identificadas', sa.Text(), nullable=True))
    op.add_column('diagnostico', op.Column('solucao_proposta', sa.Text(), nullable=True))
    op.add_column('diagnostico', op.Column('validacao_bant', postgresql.JSONB(), nullable=True))
