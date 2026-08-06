from .base import BaseAgent


class ValidarRespostaAgent(BaseAgent):
    max_tokens = 350

    def invoke(self, pergunta: str, resposta: str) -> dict:
        from .prompts import PROMPT_VALIDA_RESPOSTA
        prompt = f"{PROMPT_VALIDA_RESPOSTA}\n\nPergunta: {pergunta}\nResposta: {resposta}"
        return super().invoke(prompt)
