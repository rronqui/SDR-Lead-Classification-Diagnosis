"""Alter objetivo and indicador columns to Text type

Revision ID: 003
Revises: 002
Create Date: 2024-01-29 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('perguntas_diagnostico', 'objetivo',
                    existing_type=sa.String(100),
                    type_=sa.Text(),
                    existing_nullable=True)
    op.alter_column('perguntas_diagnostico', 'indicador',
                    existing_type=sa.String(50),
                    type_=sa.Text(),
                    existing_nullable=True)


def downgrade() -> None:
    op.alter_column('perguntas_diagnostico', 'objetivo',
                    existing_type=sa.Text(),
                    type_=sa.String(100),
                    existing_nullable=True)
    op.alter_column('perguntas_diagnostico', 'indicador',
                    existing_type=sa.Text(),
                    type_=sa.String(50),
                    existing_nullable=True)
