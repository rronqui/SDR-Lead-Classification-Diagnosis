import json
from typing import Any

from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_openrouter import ChatOpenRouter


class BaseAgent:
    max_tokens: int = 1000

    def __init__(self):
        from src.api.config import settings
        model_name = getattr(settings, "OPENROUTER_MODEL", "openai/gpt-4o-mini")

        self.llm = ChatOpenRouter(
            model=model_name,
            temperature=0.2,
            max_tokens=self.max_tokens,
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
        )
        self.parser = JsonOutputParser()

    def invoke(self, prompt: str) -> dict[str, Any]:
        messages = [
            SystemMessage(content=prompt),
        ]
        response = self.llm.invoke(messages)
        content = response.content

        if isinstance(content, str):
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON", "raw": content}
