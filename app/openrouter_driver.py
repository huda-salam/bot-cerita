from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import json
import urllib.request

from .config import settings

class OpenRouterError(RuntimeError):
    pass

@dataclass(frozen=True)
class OpenRouterResponse:
    text: str
    raw: dict[str, Any]

class OpenRouterDriver:
    name = "openrouter"

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or settings.openrouter_api_key
        self.base_url = (base_url or settings.openrouter_base_url).rstrip("/")

    async def generate(self, messages: list[dict[str, str]], model: str, *, max_tokens: int | None = None, temperature: float | None = None, response_format: dict[str, Any] | None = None) -> OpenRouterResponse:
        if not self.api_key:
            raise OpenRouterError("OPENROUTER_API_KEY is required")
        payload: dict[str, Any] = {"model": model, "messages": messages, "max_tokens": max_tokens or settings.max_tokens}
        if temperature is not None:
            payload["temperature"] = temperature
        if response_format is not None:
            payload["response_format"] = response_format
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(f"{self.base_url}/chat/completions", data=data, headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json", "HTTP-Referer": "https://github.com/huda-salam/bot-cerita", "X-Title": "Bot Cerita"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=settings.llm_timeout_seconds) as response:
                raw = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise OpenRouterError(f"OpenRouter request failed: {exc}") from exc
        try:
            text = raw["choices"][0]["message"].get("content") or ""
        except (KeyError, IndexError, TypeError) as exc:
            raise OpenRouterError(f"Unexpected OpenRouter response: {raw}") from exc
        return OpenRouterResponse(text=text, raw=raw)
