from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ImageProviderCapabilities:
    text_to_image: bool = True
    image_to_image: bool = False
    multi_reference: bool = False
    character_reference: bool = False
    style_reference: bool = False
    inpainting: bool = False
    seed: bool = False

CAPABILITIES: dict[str, ImageProviderCapabilities] = {
    "mock": ImageProviderCapabilities(text_to_image=True),
    "openai_compatible": ImageProviderCapabilities(text_to_image=True),
}

def get_capabilities(provider: str) -> ImageProviderCapabilities:
    return CAPABILITIES.get(provider, ImageProviderCapabilities(text_to_image=False))

def supports_reference_generation(provider: str) -> bool:
    c = get_capabilities(provider)
    return c.multi_reference or c.character_reference or c.image_to_image
