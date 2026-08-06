from typing import TypedDict


class NewLeadState(TypedDict):
    lead_id: str
    numero_whatsapp: str
    nome: str
    empresa: str | None
    dominio: str | None
    cargo: str | None
    dados_empresa: dict | None
    dados_linkedin: dict | None
    primeira_pergunta: dict | None
    messages: list[dict]


class MainChatState(TypedDict):
    lead_id: str
    posicao: int
    max_perguntas: int
    tentativas: int
    resposta_atual: str
    dados_empresa: dict | None
    dados_linkedin: dict | None
    historico: list[dict]
    validacao: dict | None
    proxima_pergunta: dict | None
    classificacao: dict | None
    diagnostico: dict | None
    mensagem_fechamento: str | None
    must_continue: bool
    messages: list[dict]
