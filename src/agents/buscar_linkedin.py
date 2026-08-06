import json

from .base import BaseAgent


class BuscarLinkedInAgent(BaseAgent):
    max_tokens = 1500

    def invoke(self, nome_lead: str, cargo_informado: str, empresa_informada: str, pesquisa_serpapi: list[dict] | None = None) -> dict:
        from .prompts import PROMPT_BUSCAR_LINKEDIN
        prompt = PROMPT_BUSCAR_LINKEDIN.format(
            nome_lead=nome_lead,
            cargo_informado=cargo_informado,
            empresa_informada=empresa_informada,
            pesquisa_serpapi=json.dumps(pesquisa_serpapi, ensure_ascii=False) if pesquisa_serpapi else "Nenhuma pesquisa realizada",
        )
        return super().invoke(prompt)
