import uuid

from pydantic import BaseModel, ConfigDict, field_validator


class LeadCreate(BaseModel):
    numero_whatsapp: str
    nome: str
    email: str | None = None
    empresa: str | None = None
    cargo: str | None = None
    dominio_empresa: str | None = None

    @field_validator("numero_whatsapp")
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        return v.strip().lstrip("+")


class LeadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    numero_whatsapp: str
    nome: str
    email: str | None
    empresa: str | None
    dominio_empresa: str | None
    cargo: str | None
    classificacao: str | None
    score: int | None
    status: str
    posicao_pergunta: int


class ChatMessageRequest(BaseModel):
    lead_id: uuid.UUID
    mensagem: str


class WebhookZAPIRequest(BaseModel):
    instance_id: str
    phone: str
    message: str
    type: str


class InteracaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    lead_id: uuid.UUID
    tipo: str
    mensagem: str | None
    posicao: int | None


class DiagnosticoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    lead_id: uuid.UUID
    markdown: str


__all__ = [
    "LeadCreate",
    "LeadResponse",
    "ChatMessageRequest",
    "WebhookZAPIRequest",
    "InteracaoResponse",
    "DiagnosticoResponse",
]
