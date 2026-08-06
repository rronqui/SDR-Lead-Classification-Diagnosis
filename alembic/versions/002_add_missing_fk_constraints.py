"""Add missing FK constraints

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00

"""
from typing import Sequence, Union

from alembic import op

revision: str = '002'
down_revision: Union[str, None] = '0e974bdce17a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # All foreign keys are already created in the initial migration (001_initial.py)
    # This migration is kept for historical purposes but no longer needs to create constraints
    pass


def downgrade() -> None:
    op.drop_constraint('perguntas_diagnostico_lead_id_fkey', 'perguntas_diagnostico', type_='foreignkey')
    op.drop_constraint('interacoes_chatboot_lead_id_fkey', 'interacoes_chatboot', type_='foreignkey')