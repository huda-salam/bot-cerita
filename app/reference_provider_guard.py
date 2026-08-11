from __future__ import annotations
from dataclasses import dataclass
from .image_provider_capabilities import get_capabilities

@dataclass(frozen=True)
class ReferenceRequirements:
    character_reference: bool = False
    multi_reference: bool = False
    style_reference: bool = False
    image_to_image: bool = False

class UnsupportedReferenceCapability(ValueError):
    pass

def validate_reference_capabilities(provider_name: str, requirements: ReferenceRequirements) -> None:
    caps = get_capabilities(provider_name)
    fields = ("character_reference", "multi_reference", "style_reference", "image_to_image")
    missing = [name for name in fields if getattr(requirements, name) and not getattr(caps, name)]
    if missing:
        raise UnsupportedReferenceCapability(f"Provider '{provider_name}' does not advertise required capabilities: {', '.join(missing)}")
