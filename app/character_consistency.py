from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class IdentityAnchors:
    character_id: str
    face: list[str] = field(default_factory=list)
    hair: list[str] = field(default_factory=list)
    body: list[str] = field(default_factory=list)
    outfit: list[str] = field(default_factory=list)
    accessories: list[str] = field(default_factory=list)
    palette: list[str] = field(default_factory=list)
    style: list[str] = field(default_factory=list)
    forbidden_changes: list[str] = field(default_factory=list)

@dataclass(frozen=True)
class ConsistencyCheck:
    character_id: str
    score: float
    dimensions: dict[str, float]
    warnings: list[str] = field(default_factory=list)

def build_identity_anchors(character_id: str, profile: dict[str, Any]) -> IdentityAnchors:
    return IdentityAnchors(character_id=character_id, face=list(profile.get('face', [])), hair=list(profile.get('hair', [])), body=list(profile.get('body', [])), outfit=list(profile.get('outfit', [])), accessories=list(profile.get('accessories', [])), palette=list(profile.get('palette', [])), style=list(profile.get('style', [])), forbidden_changes=list(profile.get('forbidden_changes', [])))

def evaluate_identity(character_id: str, observed: dict[str, float], anchors: IdentityAnchors) -> ConsistencyCheck:
    dimensions={k:max(0.0,min(10.0,float(v))) for k,v in observed.items()}; score=sum(dimensions.values())/len(dimensions) if dimensions else 0.0; warnings=[]
    if dimensions.get('face',10)<7: warnings.append('face identity drift')
    if dimensions.get('hair',10)<7: warnings.append('hair identity drift')
    if dimensions.get('outfit',10)<7: warnings.append('outfit continuity drift')
    return ConsistencyCheck(character_id,score,dimensions,warnings)
