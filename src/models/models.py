import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Lead(Base):
    __tablename__ = "lead"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero_whatsapp: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    empresa: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dominio_empresa: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cargo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    classificacao: Mapped[str | None] = mapped_column(String(20), nullable=True)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="novo")
    posicao_pergunta: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    perguntas_diagnostico: Mapped[list["PerguntaDiagnostico"]] = relationship(
        "PerguntaDiagnostico", back_populates="lead", cascade="all, delete-orphan"
    )
    diagnostico: Mapped["Diagnostico"] = relationship(
        "Diagnostico", back_populates="lead", uselist=False, cascade="all, delete-orphan"
    )
    interacoes: Mapped[list["InteracaoChatboot"]] = relationship(
        "InteracaoChatboot", back_populates="lead", cascade="all, delete-orphan"
    )
    info_empresa: Mapped["InfoInternetEmpresa"] = relationship(
        "InfoInternetEmpresa", back_populates="lead", uselist=False, cascade="all, delete-orphan"
    )
    info_contato: Mapped["InfoInternetContato"] = relationship(
        "InfoInternetContato", back_populates="lead", uselist=False, cascade="all, delete-orphan"
    )


class PerguntaDiagnostico(Base):
    __tablename__ = "perguntas_diagnostico"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lead.id"), nullable=False)
    posicao: Mapped[int] = mapped_column(Integer, nullable=False)
    pergunta: Mapped[str] = mapped_column(Text, nullable=False)
    objetivo: Mapped[str | None] = mapped_column(Text, nullable=True)
    indicador: Mapped[str | None] = mapped_column(Text, nullable=True)
    resposta: Mapped[str | None] = mapped_column(Text, nullable=True)
    validada: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="perguntas_diagnostico")

    def __init__(self, **kwargs):
        kwargs.setdefault("validada", False)
        super().__init__(**kwargs)


class Diagnostico(Base):
    __tablename__ = "diagnostico"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lead.id"), nullable=False)
    markdown: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="diagnostico")


class InteracaoChatboot(Base):
    __tablename__ = "interacoes_chatboot"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lead.id"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    mensagem: Mapped[str | None] = mapped_column(Text, nullable=True)
    posicao: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="interacoes")


class InfoInternetEmpresa(Base):
    __tablename__ = "info_internet_empresa"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lead.id"), nullable=False)
    razao_social: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nome_fantasia: Mapped[str | None] = mapped_column(String(255), nullable=True)
    setor: Mapped[str | None] = mapped_column(Text, nullable=True)
    tamanho: Mapped[str | None] = mapped_column(String(50), nullable=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    fonte: Mapped[str | None] = mapped_column(String(50), nullable=True)
    dados_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="info_empresa")


class InfoInternetContato(Base):
    __tablename__ = "info_internet_contato"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lead.id"), nullable=False)
    linkedin_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cargo_confirmado: Mapped[bool | None] = mapped_column(default=None)
    empresa_confirmada: Mapped[bool | None] = mapped_column(default=None)
    status_validacao: Mapped[str | None] = mapped_column(String(20), nullable=True)
    dados_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="info_contato")
