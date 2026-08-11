from __future__ import annotations
from dataclasses import dataclass
from .image_provider_capabilities import ImageProviderCapabilities, get_capabilities

@dataclass(frozen=True)
class ProviderRequirement:
    text_to_image: bool = True
    image_to_image: bool = False
    multi_reference: bool = False
    character_reference: bool = False
    style_reference: bool = False
    inpainting: bool = False
    seed: bool = False

@dataclass(frozen=True)
class ProviderCandidate:
    name: str
    capabilities: ImageProviderCapabilities
    priority: int = 0

def _score(requirement: ProviderRequirement, candidate: ProviderCandidate) -> tuple[int, int]:
    fields=("text_to_image","image_to_image","multi_reference","character_reference","style_reference","inpainting","seed")
    missing=sum(bool(getattr(requirement,f)) and not bool(getattr(candidate.capabilities,f)) for f in fields)
    if missing:return (-1000*missing,candidate.priority)
    bonus=sum(bool(getattr(requirement,f)) and bool(getattr(candidate.capabilities,f)) for f in fields)
    return (bonus,candidate.priority)

def choose_provider(requirement: ProviderRequirement, provider_names: list[str], priorities: dict[str,int] | None=None) -> ProviderCandidate | None:
    priorities=priorities or {}
    candidates=[ProviderCandidate(n,get_capabilities(n),priorities.get(n,0)) for n in provider_names]
    valid=[c for c in candidates if _score(requirement,c)[0]>=0]
    return max(valid,key=lambda c:_score(requirement,c)) if valid else None
