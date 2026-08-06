from typing import Literal

from pydantic import BaseModel


class ValidarRespostaInput(BaseModel):
    pergunta: str
    resposta: str


class ValidarRespostaOutput(BaseModel):
    valido: bool
    analise: str
    feedback_usuario: str | None


class GerarPerguntasInput(BaseModel):
    max_perguntas: int
    posicao_atual: int
    historico: list[dict] = []
    dados_empresa: dict | None = None
    dados_linkedin: dict | None = None


class GerarPerguntasOutput(BaseModel):
    NUMERO_PERGUNTA: str
    PERGUNTA: str
    OBJETIVO: str
    INDICADOR: str


class BuscarEmpresaInput(BaseModel):
    nome_empresa: str
    dominio: str
    pesquisa_serpapi: list[dict] | dict | None = None


class BuscarEmpresaOutput(BaseModel):
    razao_social: str
    nome_fantasia: str
    tamanho: str
    pensamento_logico: str
    setor_atuacao: str
    score_sdr: Literal["Alto", "Médio", "Baixo"]
    motivacao_score: str
    principais_dores_inferidas: str
    sugestao_de_abordagem: str
    confianca_da_ia: str


class BuscarLinkedInInput(BaseModel):
    nome_lead: str
    cargo_informado: str
    empresa_informada: str
    pesquisa_serpapi: list[dict] | None = None


class BuscarLinkedInOutput(BaseModel):
    pensamentos_logico: str
    perfil_linkedin_url: str
    cargo_confirmado: bool
    empresa_confirmada: bool
    status_validacao: Literal["Validado", "Inconsistente", "Não Encontrado"]
    confianca_da_ia: str
    resumo_biografico: str


class ClassificaLeadInput(BaseModel):
    dados_empresa: dict
    dados_linkedin: dict
    historico_respostas: list[dict]
    posicao_final: int


class ClassificaLeadOutput(BaseModel):
    classificacao: Literal["A", "B", "C"]
    score: int
    raciocinio: str
    proximo_passo_venda: str


class GerarDiagnosticoInput(BaseModel):
    dados_empresa: dict
    dados_linkedin: dict
    historico_respostas: list[dict]
    classificacao: dict


class GerarDiagnosticoOutput(BaseModel):
    markdown: str


class MsgFechamentoInput(BaseModel):
    diagnostico: dict
    nome_lead: str
    dados_empresa: dict


class MsgFechamentoOutput(BaseModel):
    mensagem: str
