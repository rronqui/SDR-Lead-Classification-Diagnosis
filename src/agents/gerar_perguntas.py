import json

from .base import BaseAgent


class GerarPerguntasAgent(BaseAgent):
    max_tokens = 20_000

    def invoke(
        self,
        max_perguntas: int,
        historico: list[dict] | str,
        dados_empresa: dict | None,
        dados_linkedin: dict | None,
    ) -> dict:
        from .prompts import PROMPT_GERAR_PERGUNTAS

        if isinstance(historico, str):
            historico_str = historico
        else:
            historico_str = json.dumps(historico, ensure_ascii=False)

        prompt = PROMPT_GERAR_PERGUNTAS.format(
            max_perguntas=max_perguntas,
            historico=historico_str,
            dados_empresa=json.dumps(dados_empresa, ensure_ascii=False) if dados_empresa else "N/A",
            dados_linkedin=json.dumps(dados_linkedin, ensure_ascii=False) if dados_linkedin else "N/A",
        )
        return super().invoke(prompt)
