from __future__ import annotations

import copy
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
        cleaned = content.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        try:
            return schema.model_validate(json.loads(cleaned.strip()))
        except Exception as exc:
            raise LLMError(f"Invalid structured output: {exc}; raw={content[:3000]}") from exc


class AnthropicDriver(LLMDriver):
    name = "anthropic"

    async def generate(self, system, user, schema, model):
        if not settings.anthropic_api_key:
            raise LLMError("ANTHROPIC_API_KEY is not configured")
        payload = {
            "model": model,
            "max_tokens": settings.max_tokens,
            "system": system + "\n\nReturn ONLY valid JSON matching the requested schema.",
            "messages": [{"role": "user", "content": user}],
        }
        headers = {
            "x-api-key": settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
            response = await client.post(settings.anthropic_base_url.rstrip("/") + "/v1/messages", headers=headers, json=payload)
        if response.status_code >= 400:
            raise LLMError(f"Anthropic error {response.status_code}: {response.text[:2000]}")
        data = response.json()
        content = "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text")
        return self.parse(content, schema)


class OpenAICompatibleDriver(LLMDriver):
    """OpenRouter or any OpenAI-compatible endpoint, including Ollama."""

    def __init__(self, name: str):
        self.name = name

    @staticmethod
    def _extract_content(data: dict) -> str:
        choices = data.get("choices")
        if not choices:
            error = data.get("error")
            if error:
                raise LLMError(f"OpenAI-compatible error: {json.dumps(error, ensure_ascii=False)[:3000]}")
            raise LLMError(f"OpenAI-compatible response missing 'choices': {json.dumps(data, ensure_ascii=False)[:3000]}")
        message = choices[0].get("message") or {}
        content = message.get("content")
        if isinstance(content, list):
            content = "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content)
        if not content and message.get("reasoning_content"):
            raise LLMError("OpenAI-compatible model returned reasoning content but no final message content")
        if not content:
            raise LLMError(f"OpenAI-compatible response has empty message content: {json.dumps(data, ensure_ascii=False)[:3000]}")
        return content

    @staticmethod
    def _strict_json_schema(schema: type[BaseModel]) -> dict:
        """Convert Pydantic's schema into a provider-friendly strict JSON Schema.

        OpenRouter documents strict structured outputs as response_format.type=json_schema
        with strict=true. Strict providers generally require object properties to be
        explicitly listed in required and reject undeclared properties.
        """
        result = copy.deepcopy(schema.model_json_schema())

        def normalize(node: object):
            if not isinstance(node, dict):
                return
            if node.get("type") == "object" or "properties" in node:
                properties = node.get("properties", {})
                node["additionalProperties"] = False
                if properties:
                    node["required"] = list(properties.keys())
                for child in properties.values():
                    normalize(child)
            for child in node.get("$defs", {}).values():
                normalize(child)
            if "items" in node:
                normalize(node["items"])
            for child in node.get("anyOf", []):
                normalize(child)
            for child in node.get("oneOf", []):
                normalize(child)
            for child in node.get("allOf", []):
                normalize(child)

        normalize(result)
        return result

    async def generate(self, system, user, schema, model):
        api_key = settings.openrouter_api_key if self.name == "openrouter" else settings.local_llm_api_key
        if not api_key and self.name != "ollama":
            raise LLMError(f"API key is not configured for {self.name}")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        if self.name == "openrouter":
            headers["HTTP-Referer"] = "https://github.com/huda-salam/bot-cerita"
            headers["X-Title"] = "Bot Cerita"
        base_url = settings.openrouter_base_url if self.name == "openrouter" else settings.local_llm_base_url
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": system + "\n\nReturn the requested object. Follow the JSON schema exactly; do not use markdown fences.",
                },
                {"role": "user", "content": user},
            ],
            "max_tokens": settings.max_tokens,
        }
        # OpenRouter structured outputs are endpoint-dependent. Requiring the
        # provider to support the requested parameter prevents silent fallback
        # to an endpoint that merely treats the schema as a prompt hint.
        if self.name == "openrouter":
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": schema.__name__,
                    "strict": True,
                    "schema": self._strict_json_schema(schema),
                },
            }
            payload["provider"] = {"require_parameters": True}

        async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
            response = await client.post(base_url.rstrip("/") + "/chat/completions", headers=headers, json=payload)
        if response.status_code >= 400:
            raise LLMError(f"{self.name} error {response.status_code}: {response.text[:5000]}")
        try:
            data = response.json()
        except ValueError as exc:
            raise LLMError(f"{self.name} returned non-JSON HTTP {response.status_code}: {response.text[:3000]}") from exc
        content = self._extract_content(data)
        return self.parse(content, schema)


class ModelRouter:
    def __init__(self):
        self.drivers = {
            "anthropic": AnthropicDriver(),
            "openrouter": OpenAICompatibleDriver("openrouter"),
            "ollama": OpenAICompatibleDriver("ollama"),
        }

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
