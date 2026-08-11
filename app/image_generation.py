from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

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
        return [GeneratedImage(provider=self.name, model=model, metadata={"prompt": request.prompt, "references": len(request.reference_assets)}) for _ in range(request.count)]

class ImageRouter:
    def __init__(self, drivers: dict[str, ImageDriver] | None = None, aliases: dict[str, tuple[str, str]] | None = None):
        self.drivers = drivers or {"mock": MockImageDriver()}
        self.aliases = aliases or {"image-draft": ("mock", "mock")}
    def resolve(self, model: str) -> tuple[ImageDriver, str]:
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
    async def generate(self, request: ImageRequest, model: str = "image-draft") -> list[GeneratedImage]:
        driver, provider_model = self.resolve(model)
        return await driver.generate(request, provider_model)

image_router = ImageRouter()
