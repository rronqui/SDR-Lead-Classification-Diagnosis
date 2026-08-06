import json

from .base import BaseAgent


class ClassificaLeadAgent(BaseAgent):
    max_tokens = 1500

    def invoke(self, dados_completos: dict) -> dict:
        from .prompts import PROMPT_CLASSIFICA_LEAD
        prompt = PROMPT_CLASSIFICA_LEAD.format(
            dados_completos=json.dumps(dados_completos, ensure_ascii=False)
        )
        return super().invoke(prompt)
