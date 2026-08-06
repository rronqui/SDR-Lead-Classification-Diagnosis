import json

from .base import BaseAgent


class BuscarEmpresaAgent(BaseAgent):
    max_tokens = 1500

    def invoke(self, nome_empresa: str, dominio: str, pesquisa_serpapi: list[dict] | dict | None) -> dict:
        from .prompts import PROMPT_BUSCAR_EMPRESA
        prompt = PROMPT_BUSCAR_EMPRESA.format(
            nome_empresa=nome_empresa,
            dominio=dominio,
            pesquisa_serpapi=json.dumps(pesquisa_serpapi, ensure_ascii=False) if pesquisa_serpapi else "N/A",
        )
        return super().invoke(prompt)
