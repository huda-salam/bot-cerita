from __future__ import annotations
import os
from typing import Any
from .image_provider import ImageGenerationRequest, ImageGenerationResult

class OpenAICompatibleImageProvider:
    """Generic OpenAI-compatible image adapter for text-to-image APIs."""
    name = "openai_compatible"

    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = (base_url or os.getenv("IMAGE_API_BASE_URL", "")).rstrip("/")
        self.api_key = api_key or os.getenv("IMAGE_API_KEY", "")

    async def generate(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        if not self.base_url or not self.api_key:
            return ImageGenerationResult(provider=self.name, model=request.model or "unknown", status="not_configured", metadata={"error":"IMAGE_API_BASE_URL and IMAGE_API_KEY are required"})
        try:
            import httpx
        except ImportError as exc:
            raise RuntimeError("httpx is required for the HTTP image provider") from exc
        payload: dict[str, Any] = {"model": request.model or os.getenv("IMAGE_MODEL", ""), "prompt": request.prompt, "size": f"{request.width}x{request.height}", "n": 1}
        if request.options.get("response_format"):
            payload["response_format"] = request.options["response_format"]
        async with httpx.AsyncClient(timeout=float(os.getenv("IMAGE_API_TIMEOUT", "120"))) as client:
            response = await client.post(f"{self.base_url}/images/generations", headers={"Authorization": f"Bearer {self.api_key}", "Content-Type":"application/json"}, json=payload)
            response.raise_for_status()
            data = response.json()
        item = (data.get("data") or [{}])[0]
        metadata = {"response": {k:v for k,v in data.items() if k != "data"}}
        if item.get("b64_json"):
            metadata["image_base64"] = item["b64_json"]
        return ImageGenerationResult(provider=self.name, model=payload["model"], status="completed", url=item.get("url", ""), seed=item.get("seed"), metadata=metadata)
