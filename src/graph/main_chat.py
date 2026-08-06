from langgraph.graph import END, StateGraph

from src.graph import nodes
from src.graph.states import MainChatState


def create_main_chat_graph() -> StateGraph:
    graph = StateGraph(MainChatState)

    graph.add_node("validar_resposta", nodes.validar_resposta_node)
    graph.add_node("reenviar_pergunta", nodes.reenviar_pergunta_node)
    graph.add_node("gerar_proxima_pergunta", nodes.gerar_proxima_pergunta_node)
    graph.add_node("classificar_lead", nodes.classificar_lead_node)
    graph.add_node("gerar_diagnostico", nodes.gerar_diagnostico_node)
    graph.add_node("gerar_fechamento", nodes.gerar_fechamento_node)
    graph.add_node("enviar_pergunta", nodes.enviar_pergunta_node)

    graph.set_entry_point("validar_resposta")

    graph.add_conditional_edges(
        "validar_resposta",
        nodes.check_validacao,
        {
            "reenviar_pergunta": "reenviar_pergunta",
            "continuar_fluxo": "gerar_proxima_pergunta",
        },
    )

    graph.add_edge("reenviar_pergunta", END)

    graph.add_conditional_edges(
        "gerar_proxima_pergunta",
        nodes.check_fim_entrevista,
        {
            "classificar_lead": "classificar_lead",
            "enviar_pergunta": "enviar_pergunta",
        },
    )

    graph.add_edge("classificar_lead", "gerar_diagnostico")
    graph.add_edge("gerar_diagnostico", "gerar_fechamento")
    graph.add_edge("gerar_fechamento", END)
    graph.add_edge("enviar_pergunta", END)

    return graph


MainChatGraph = create_main_chat_graph().compile()
