from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Protocol
from .visual_context import GenerationContext

@dataclass(frozen=True)
class ImageGenerationRequest:
    prompt: str
    context: GenerationContext
    width: int = 1024
    height: int = 1024
    model: str | None = None
    options: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class ImageGenerationResult:
    provider: str
    model: str
    status: str
    url: str = ""
    file_path: str = ""
    seed: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

class ImageProvider(Protocol):
    name: str
    async def generate(self, request: ImageGenerationRequest) -> ImageGenerationResult: ...

class MockImageProvider:
    name = "mock"
    async def generate(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        return ImageGenerationResult(provider=self.name, model=request.model or "mock-v1", status="accepted", metadata={"prompt_context": request.context.prompt_context(), "note": "No external image model called."})

class ImageProviderRegistry:
    def __init__(self): self._providers = {}
    def register(self, provider: ImageProvider): self._providers[provider.name] = provider
    def get(self, name: str) -> ImageProvider:
        if name not in self._providers: raise KeyError(f"Image provider not registered: {name}")
        return self._providers[name]
    def names(self): return sorted(self._providers)

registry = ImageProviderRegistry()
registry.register(MockImageProvider())
