"""Create initial tables

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'lead',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('numero_whatsapp', sa.String(20), unique=True, nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('empresa', sa.String(255), nullable=True),
        sa.Column('dominio_empresa', sa.String(255), nullable=True),
        sa.Column('cargo', sa.String(100), nullable=True),
        sa.Column('classificacao', sa.String(1), nullable=True),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(20), default='novo'),
        sa.Column('posicao_pergunta', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('idx_lead_numero', 'lead', ['numero_whatsapp'])
    op.create_index('idx_lead_status', 'lead', ['status'])

    op.create_table(
        'perguntas_diagnostico',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('lead_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lead.id'), nullable=False),
        sa.Column('posicao', sa.Integer(), nullable=False),
        sa.Column('pergunta', sa.Text(), nullable=False),
        sa.Column('objetivo', sa.String(100), nullable=True),
        sa.Column('indicador', sa.String(50), nullable=True),
        sa.Column('resposta', sa.Text(), nullable=True),
        sa.Column('validada', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('idx_perguntas_lead', 'perguntas_diagnostico', ['lead_id'])

    op.create_table(
        'diagnostico',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('lead_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lead.id'), nullable=False),
        sa.Column('markdown', sa.Text(), nullable=False),
        sa.Column('panaram_brief', sa.Text(), nullable=True),
        sa.Column('dores_identificadas', sa.Text(), nullable=True),
        sa.Column('solucao_proposta', sa.Text(), nullable=True),
        sa.Column('validacao_bant', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('idx_diagnostico_lead', 'diagnostico', ['lead_id'])

    op.create_table(
        'interacoes_chatboot',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('lead_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lead.id'), nullable=False),
        sa.Column('tipo', sa.String(20), nullable=False),
        sa.Column('mensagem', sa.Text(), nullable=True),
        sa.Column('posicao', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('idx_interacoes_lead', 'interacoes_chatboot', ['lead_id'])

    op.create_table(
        'info_internet_empresa',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('lead_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lead.id'), nullable=False),
        sa.Column('razao_social', sa.String(255), nullable=True),
        sa.Column('nome_fantasia', sa.String(255), nullable=True),
        sa.Column('setor', sa.String(100), nullable=True),
        sa.Column('tamanho', sa.String(50), nullable=True),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('fonte', sa.String(50), nullable=True),
        sa.Column('dados_json', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('idx_info_empresa_lead', 'info_internet_empresa', ['lead_id'])

    op.create_table(
        'info_internet_contato',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('lead_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lead.id'), nullable=False),
        sa.Column('linkedin_url', sa.String(500), nullable=True),
        sa.Column('cargo_confirmado', sa.Boolean(), nullable=True),
        sa.Column('empresa_confirmada', sa.Boolean(), nullable=True),
        sa.Column('status_validacao', sa.String(20), nullable=True),
        sa.Column('dados_json', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('idx_info_contato_lead', 'info_internet_contato', ['lead_id'])


def downgrade() -> None:
    op.drop_table('info_internet_contato')
    op.drop_table('info_internet_empresa')
    op.drop_table('interacoes_chatboot')
    op.drop_table('diagnostico')
    op.drop_table('perguntas_diagnostico')
    op.drop_table('lead')