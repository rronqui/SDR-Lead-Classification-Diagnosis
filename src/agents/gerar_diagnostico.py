import json

from .base import BaseAgent


class GerarDiagnosticoAgent(BaseAgent):
    max_tokens = 3500

    def invoke(self, dados_entrada: dict) -> dict:
        from .prompts import PROMPT_DIAGNOSTICO
        prompt = PROMPT_DIAGNOSTICO.format(
            dados_entrada=json.dumps(dados_entrada, ensure_ascii=False)
        )
        response = super().invoke(prompt)
        if "error" not in response:
            return {
                "markdown": response.get("markdown", str(response)),
            }
        return {
            "markdown": response.get("raw", str(response)),
        }
