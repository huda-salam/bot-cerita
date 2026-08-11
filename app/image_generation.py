from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
import os

class ImageGenerationError(RuntimeError):
    pass

@dataclass(frozen=True)
class ImageRequest:
    prompt: str
    negative_prompt: str = ""
    reference_assets: list[dict[str, Any]] = field(default_factory=list)
    width: int = 1024
    height: int = 1024
    count: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class GeneratedImage:
    provider: str
    model: str
    url: str = ""
    file_path: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

class ImageDriver(ABC):
    name: str
    @abstractmethod
    async def generate(self, request: ImageRequest, model: str) -> list[GeneratedImage]:
        raise NotImplementedError

class MockImageDriver(ImageDriver):
    name = "mock"
    async def generate(self, request: ImageRequest, model: str) -> list[GeneratedImage]:
        return [GeneratedImage(self.name, model, metadata={"prompt": request.prompt, "references": len(request.reference_assets)}) for _ in range(request.count)]

class OpenAICompatibleImageDriver(ImageDriver):
    """Provider adapter boundary for OpenAI-compatible image endpoints.

    The transport is intentionally kept behind this interface. Providers that
    support reference images can consume ImageRequest.reference_assets without
    changing the story engine.
    """
    name = "openai_compatible"
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    async def generate(self, request: ImageRequest, model: str) -> list[GeneratedImage]:
        raise ImageGenerationError("Image provider transport is not enabled yet; use a concrete provider adapter")

class ImageRouter:
    def __init__(self, drivers=None, aliases=None):
        self.drivers = drivers or {"mock": MockImageDriver()}
        self.aliases = aliases or {"image-draft": ("mock", "mock")}

    def resolve(self, model: str):
        if model in self.aliases:
            provider, provider_model = self.aliases[model]
            if provider not in self.drivers:
                raise ImageGenerationError(f"Image driver '{provider}' is not configured")
            return self.drivers[provider], provider_model
        if ":" in model:
            provider, provider_model = model.split(":", 1)
            if provider in self.drivers:
                return self.drivers[provider], provider_model
        raise ImageGenerationError(f"No image driver available for model '{model}'")

    async def generate(self, request: ImageRequest, model: str = "image-draft"):
        driver, provider_model = self.resolve(model)
        return await driver.generate(request, provider_model)

def build_image_router_from_env() -> ImageRouter:
    drivers = {"mock": MockImageDriver()}
    aliases = {"image-draft": ("mock", "mock")}
    base_url = os.getenv("IMAGE_API_BASE_URL")
    api_key = os.getenv("IMAGE_API_KEY")
    if base_url and api_key:
        drivers["image_api"] = OpenAICompatibleImageDriver(base_url, api_key)
        aliases["image-production"] = ("image_api", os.getenv("IMAGE_MODEL", "image-model"))
    return ImageRouter(drivers, aliases)

image_router = build_image_router_from_env()
