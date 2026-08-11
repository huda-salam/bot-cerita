import json
import httpx
from pydantic import BaseModel
from .config import settings


class LLMError(RuntimeError):
    pass


class LLM:
    """Small provider abstraction used by the orchestrator.

    Anthropic is the default provider. OpenRouter remains available as a
    fallback for experiments with other models.
    """

    async def generate(
        self,
        system: str,
        user: str,
        schema: type[BaseModel],
        model: str = "",
    ) -> BaseModel:
        chosen = model or settings.default_model
        if settings.llm_provider.lower() == "anthropic":
            return await self._anthropic(system, user, schema, chosen)
        return await self._openrouter(system, user, schema, chosen)

    async def _anthropic(self, system, user, schema, model):
        if not settings.anthropic_api_key:
            raise LLMError(
                "ANTHROPIC_API_KEY is not configured. A Claude.ai Pro/Max subscription "
                "is useful for Claude/Claude Code, but the application needs Anthropic "
                "API access (or set LLM_PROVIDER=openrouter)."
            )

        url = settings.anthropic_base_url.rstrip("/") + "/v1/messages"
        headers = {
            "x-api-key": settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": model,
            "max_tokens": 8192,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }

        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code >= 400:
            raise LLMError(f"Anthropic error {response.status_code}: {response.text[:1000]}")

        data = response.json()
        content = "".join(
            block.get("text", "")
            for block in data.get("content", [])
            if block.get("type") == "text"
        )
        return self._parse(content, schema)

    async def _openrouter(self, system, user, schema, model):
        if not settings.openrouter_api_key:
            raise LLMError("OPENROUTER_API_KEY is not configured")

        url = settings.openrouter_base_url.rstrip("/") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Bot Cerita",
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {"type": "json_object"},
        }

        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code >= 400:
            raise LLMError(f"OpenRouter error {response.status_code}: {response.text[:1000]}")

        content = response.json()["choices"][0]["message"]["content"]
        return self._parse(content, schema)

    @staticmethod
    def _parse(content: str, schema: type[BaseModel]) -> BaseModel:
        try:
            return schema.model_validate(json.loads(content))
        except Exception as exc:
            raise LLMError(
                f"Invalid structured output: {exc}; raw={content[:2000]}"
            ) from exc


llm = LLM()
