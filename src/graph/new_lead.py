from langgraph.graph import END, StateGraph

from src.graph import nodes
from src.graph.states import NewLeadState


def create_new_lead_graph() -> StateGraph:
    graph = StateGraph(NewLeadState)

    graph.add_node("buscar_empresa", nodes.buscar_empresa_node)
    graph.add_node("buscar_linkedin", nodes.buscar_linkedin_node)
    graph.add_node("gerar_pergunta", nodes.gerar_primeira_pergunta_node)
    graph.add_node("welcome_message", nodes.criar_welcome_message)

    graph.set_entry_point("buscar_empresa")
    graph.add_edge("buscar_empresa", "buscar_linkedin")
    graph.add_edge("buscar_linkedin", "gerar_pergunta")
    graph.add_edge("gerar_pergunta", "welcome_message")
    graph.add_edge("welcome_message", END)

    return graph


NewLeadGraph = create_new_lead_graph().compile()
