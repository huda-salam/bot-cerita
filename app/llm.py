from __future__ import annotations

import json
from abc import ABC, abstractmethod
import httpx
from pydantic import BaseModel
from .config import settings


class LLMError(RuntimeError):
    pass


class LLMDriver(ABC):
    name: str

    @abstractmethod
    async def generate(self, system: str, user: str, schema: type[BaseModel], model: str) -> BaseModel:
        raise NotImplementedError

    @staticmethod
    def parse(content: str, schema: type[BaseModel]) -> BaseModel:
        try:
            return schema.model_validate(json.loads(content))
        except Exception as exc:
            raise LLMError(f"Invalid structured output: {exc}; raw={content[:2000]}") from exc


class AnthropicDriver(LLMDriver):
    name = "anthropic"

    async def generate(self, system, user, schema, model):
        if not settings.anthropic_api_key:
            raise LLMError("ANTHROPIC_API_KEY is not configured")
        payload = {"model": model, "max_tokens": settings.max_tokens, "system": system + "\n\nReturn ONLY valid JSON matching the requested schema.", "messages": [{"role": "user", "content": user}]}
        headers = {"x-api-key": settings.anthropic_api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
        async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
            response = await client.post(settings.anthropic_base_url.rstrip("/") + "/v1/messages", headers=headers, json=payload)
        if response.status_code >= 400:
            raise LLMError(f"Anthropic error {response.status_code}: {response.text[:1000]}")
        data = response.json()
        content = "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text")
        return self.parse(content, schema)


class OpenAICompatibleDriver(LLMDriver):
    """OpenRouter or any OpenAI-compatible endpoint, including Ollama."""

    def __init__(self, name: str):
        self.name = name

    async def generate(self, system, user, schema, model):
        api_key = settings.openrouter_api_key if self.name == "openrouter" else settings.local_llm_api_key
        if not api_key and self.name != "ollama":
            raise LLMError(f"API key is not configured for {self.name}")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        base_url = settings.openrouter_base_url if self.name == "openrouter" else settings.local_llm_base_url
        payload = {"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}], "response_format": {"type": "json_object"}}
        async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
            response = await client.post(base_url.rstrip("/") + "/chat/completions", headers=headers, json=payload)
        if response.status_code >= 400:
            raise LLMError(f"{self.name} error {response.status_code}: {response.text[:1000]}")
        content = response.json()["choices"][0]["message"]["content"]
        return self.parse(content, schema)


class ModelRouter:
    def __init__(self):
        self.drivers = {"anthropic": AnthropicDriver(), "openrouter": OpenAICompatibleDriver("openrouter"), "ollama": OpenAICompatibleDriver("ollama")}

    def resolve(self, model: str):
        alias = settings.model_aliases.get(model)
        if alias:
            provider, provider_model = alias.split(":", 1)
            if provider not in self.drivers:
                raise LLMError(f"Unknown LLM provider: {provider}")
            return self.drivers[provider], provider_model
        if model.startswith("openrouter/"):
            return self.drivers["openrouter"], model.removeprefix("openrouter/")
        if model.startswith("ollama/"):
            return self.drivers["ollama"], model.removeprefix("ollama/")
        return self.drivers[settings.llm_provider], model

    async def generate(self, system, user, schema, model):
        driver, provider_model = self.resolve(model)
        return await driver.generate(system, user, schema, provider_model)


llm = ModelRouter()
