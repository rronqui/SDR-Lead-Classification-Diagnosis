import logging

from langsmith import traceable
from serpapi import Client

from src.api.config import settings

logger = logging.getLogger(__name__)


def formatar_historico_string(historico: list[dict]) -> str:
    """Formata o histórico como string numerada para melhor legibilidade da LLM."""
    if not historico:
        return "Nenhum histórico disponível."

    linhas = ["## Histórico de Perguntas e Respostas:"]
    for i, item in enumerate(historico, start=1):
        linhas.append(f"\n**Pergunta {i}:** {item.get('pergunta', '')}")
        linhas.append(f"**Resposta {i}:** {item.get('resposta', '')}")
        if item.get('objetivo'):
            linhas.append(f"**Objetivo {i}:** {item.get('objetivo', '')}")

    return "".join(linhas)


@traceable(name="serpapi_google_search")
def _serpapi_google_search(query: str) -> list[dict]:
    client = Client(api_key=settings.SERPAPI_API_KEY)
    result = client.search(
        engine="google",
        q=query,
        gl="br",
        google_domain="google.com.br",
        hl="pt",
    )
    return result.get("organic_results", [])


def validar_resposta_node(state: dict) -> dict:
    from src.agents import ValidarRespostaAgent

    agent = ValidarRespostaAgent()
    last_question = state.get("last_question") or ""

    resultado = agent.invoke(
        pergunta=last_question,
        resposta=state["resposta_atual"],
    )
    state["validacao"] = resultado
    return state


def check_validacao(state: dict) -> str:
    valido = state.get("validacao", {}).get("valido", True)
    tentativas = state.get("tentativas", 0)
    logger.info(f"[DEBUG check_validacao] valido={valido}, tentativas={tentativas}")
    if not valido and tentativas >= 3:
        logger.info("[DEBUG check_validacao] returning: continuar_fluxo (tentativas >= 3)")
        return "continuar_fluxo"
    if not valido:
        logger.info("[DEBUG check_validacao] returning: reenviar_pergunta")
        return "reenviar_pergunta"
    logger.info("[DEBUG check_validacao] returning: continuar_fluxo")
    return "continuar_fluxo"


def reenviar_pergunta_node(state: dict) -> dict:
    feedback = state.get("validacao", {}).get("feedback_usuario", "")
    last_question = state.get("last_question") or (state.get("historico", [])[-1]["pergunta"] if state.get("historico") else "")

    message = f"{feedback}\n\n{last_question}"
    state["messages"] = [{"type": "outgoing", "message": message}]
    state["must_continue"] = True
    state["tentativas"] = state.get("tentativas", 0) + 1
    return state


def gerar_proxima_pergunta_node(state: dict) -> dict:
    from src.agents import GerarPerguntasAgent

    agent = GerarPerguntasAgent()
    logger.info(f"[DEBUG gerar_proxima_pergunta_node] IN - posicao={state.get('posicao')}, historico_len={len(state.get('historico', []))}")
    historico_string = formatar_historico_string(state.get("historico", []))

    resultado = agent.invoke(
        max_perguntas=state["max_perguntas"],
        historico=historico_string,
        dados_empresa=state.get("dados_empresa"),
        dados_linkedin=state.get("dados_linkedin"),
    )

    logger.info(f"[DEBUG gerar_proxima_pergunta_node] OUT - resultado={resultado}")
    state["proxima_pergunta"] = resultado
    return state


def check_fim_entrevista(state: dict) -> str:
    if state["posicao"] + 1 >= state["max_perguntas"]:
        return "classificar_lead"
    return "enviar_pergunta"


def classificar_lead_node(state: dict) -> dict:
    from src.agents import ClassificaLeadAgent

    agent = ClassificaLeadAgent()
    dados_completos = {
        "dados_empresa": state.get("dados_empresa", {}),
        "dados_linkedin": state.get("dados_linkedin", {}),
        "historico_respostas": state.get("historico", []),
        "posicao_final": state["posicao"],
    }

    resultado = agent.invoke(dados_completos)
    state["classificacao"] = resultado
    return state


def gerar_diagnostico_node(state: dict) -> dict:
    from src.agents import GerarDiagnosticoAgent

    agent = GerarDiagnosticoAgent()
    dados_entrada = {
        "dados_empresa": state.get("dados_empresa", {}),
        "dados_linkedin": state.get("dados_linkedin", {}),
        "historico_respostas": state.get("historico", []),
        "classificacao": state.get("classificacao", {}),
    }

    resultado = agent.invoke(dados_entrada)
    state["diagnostico"] = resultado
    return state


def gerar_fechamento_node(state: dict) -> dict:
    from src.agents import MsgFechamentoAgent

    agent = MsgFechamentoAgent()
    resultado = agent.invoke(
        nome_lead=state.get("nome_lead", ""),
        diagnostico=state.get("diagnostico", {}),
        dados_empresa=state.get("dados_empresa", {}),
    )
    state["mensagem_fechamento"] = resultado.get("mensagem", "")
    return state


def enviar_pergunta_node(state: dict) -> dict:
    pergunta = state.get("proxima_pergunta", {}).get("PERGUNTA", "")
    state["messages"] = [{"type": "outgoing", "message": pergunta}]
    state["must_continue"] = True
    return state


@traceable(name="search_empresa_serpapi")
def buscar_empresa_node(state: dict) -> dict:
    from src.agents import BuscarEmpresaAgent

    logger.info(f"[buscar_empresa] empresa={state.get('empresa')}, dominio={state.get('dominio')}")

    agent = BuscarEmpresaAgent()

    pesquisa_serpapi = None
    if state.get("dominio"):
        try:
            query = f"{state['empresa']} {state['dominio']}"
            logger.info(f"[buscar_empresa] Executando pesquisa SerpAPI: {query}")
            pesquisa_serpapi = _serpapi_google_search(query)
            logger.info(f"[buscar_empresa] Resultados SerpAPI: {len(pesquisa_serpapi) if pesquisa_serpapi else 0}")
        except Exception as e:
            logger.error(f"[buscar_empresa] Erro na pesquisa SerpAPI: {e}")

    resultado = agent.invoke(
        nome_empresa=state.get("empresa", ""),
        dominio=state.get("dominio", ""),
        pesquisa_serpapi=pesquisa_serpapi,
    )

    state["dados_empresa"] = resultado
    return state


@traceable(name="search_linkedin_serpapi")
def buscar_linkedin_node(state: dict) -> dict:
    from src.agents import BuscarLinkedInAgent

    logger.info(f"[buscar_linkedin] nome={state.get('nome')}, empresa={state.get('empresa')}, cargo={state.get('cargo')}")

    agent = BuscarLinkedInAgent()

    pesquisa_serpapi = None
    if state.get("nome") and state.get("empresa"):
        try:
            query = f"site:linkedin.com/in {state['nome']} {state['empresa']}"
            logger.info(f"[buscar_linkedin] Executando pesquisa SerpAPI: {query}")
            pesquisa_serpapi = _serpapi_google_search(query)
            logger.info(f"[buscar_linkedin] Resultados SerpAPI: {len(pesquisa_serpapi) if pesquisa_serpapi else 0}")
        except Exception as e:
            logger.error(f"[buscar_linkedin] Erro na pesquisa SerpAPI: {e}")

    resultado = agent.invoke(
        nome_lead=state.get("nome", ""),
        cargo_informado=state.get("cargo", ""),
        empresa_informada=state.get("empresa", ""),
        pesquisa_serpapi=pesquisa_serpapi,
    )
    state["dados_linkedin"] = resultado
    logger.info(f"[buscar_linkedin] Resultado: {resultado.get('perfil_linkedin_url', 'N/A')}")
    return state


def gerar_primeira_pergunta_node(state: dict) -> dict:
    from src.agents import GerarPerguntasAgent

    agent = GerarPerguntasAgent()
    max_perguntas = settings.MAX_PERGUNTAS

    resultado = agent.invoke(
        max_perguntas=max_perguntas,
        historico=[],
        dados_empresa=state.get("dados_empresa"),
        dados_linkedin=state.get("dados_linkedin"),
    )

    state["primeira_pergunta"] = resultado
    return state


def should_continue_newlead(state: dict) -> str:
    return "generate_welcome_message"


def criar_welcome_message(state: dict) -> dict:
    pergunta = state.get("primeira_pergunta", {}).get("PERGUNTA", "")
    message = f"Olá {state.get('nome')}! Agradecemos seu interesse em nossas soluções de automação.\n\n{pergunta}"
    state["messages"] = [{"type": "outgoing", "message": message}]
    return state
