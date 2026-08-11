import json
import httpx
from pydantic import BaseModel
from .config import settings

class LLMError(RuntimeError):
    pass

class OpenRouter:
    def __init__(self):
        self.url = settings.openrouter_base_url.rstrip("/") + "/chat/completions"

    async def generate(self, system: str, user: str, schema: type[BaseModel], model: str = "") -> BaseModel:
        chosen = model or settings.default_model
        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Bot Cerita",
        }
        payload = {
            "model": chosen,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "response_format": {"type": "json_object"},
        }
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(self.url, headers=headers, json=payload)
        if response.status_code >= 400:
            raise LLMError(f"OpenRouter error {response.status_code}: {response.text[:500]}")
        content = response.json()["choices"][0]["message"]["content"]
        try:
            return schema.model_validate(json.loads(content))
        except Exception as exc:
            raise LLMError(f"Invalid structured output: {exc}; raw={content[:1000]}") from exc

llm = OpenRouter()
