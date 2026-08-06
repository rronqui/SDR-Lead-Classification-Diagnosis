import json

from .base import BaseAgent


class MsgFechamentoAgent(BaseAgent):
    max_tokens = 1000

    def invoke(self, nome_lead: str, diagnostico: dict, dados_empresa: dict) -> dict:
        from .prompts import PROMPT_FECHAMENTO
        prompt = PROMPT_FECHAMENTO.format(
            nome_lead=nome_lead,
            diagnostico=json.dumps(diagnostico, ensure_ascii=False),
            dados_empresa=json.dumps(dados_empresa, ensure_ascii=False),
        )
        response = super().invoke(prompt)
        if "error" not in response:
            return {
                "mensagem": response.get("mensagem", str(response)),
            }
        return {
            "mensagem": response.get("raw", ""),
        }
