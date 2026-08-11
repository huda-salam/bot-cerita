from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

@dataclass(frozen=True)
class GenerationLineage:
    id: str
    character_ids: list[str]
    reference_asset_ids: list[str]
    source_panel_id: str
    seed: int | None = None
    provider: str = ""
    model: str = ""
    parent_image_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class ConsistencySpec:
    character_ids: list[str]
    reference_assets: list[dict[str, Any]]
    style_bible: str = ""
    seed: int | None = None
    negative_prompt: str = ""
    continuity_notes: list[str] = field(default_factory=list)

def build_consistency_spec(character_ids, reference_assets, style_bible="", seed=None, continuity_notes=None):
    return ConsistencySpec(character_ids, reference_assets, style_bible, seed, continuity_notes=continuity_notes or [])

def augment_prompt(prompt: str, spec: ConsistencySpec) -> str:
    refs = "\n".join(f"- {r.get('file_path','')} | view={r.get('view','')} | pose={r.get('pose','')} | outfit={r.get('outfit','')} | age={r.get('age','')}" for r in spec.reference_assets)
    notes = "\n".join(f"- {x}" for x in spec.continuity_notes)
    return f"{prompt}\n\nCHARACTER CONSISTENCY\nCharacters: {', '.join(spec.character_ids) or 'none'}\nReference assets:\n{refs or '- none'}\nStyle bible:\n{spec.style_bible or '- none'}\nContinuity notes:\n{notes or '- none'}\nSeed: {spec.seed if spec.seed is not None else 'provider-managed'}\nInstruction: preserve identity and established visual anchors across panels. Treat references and continuity notes as constraints, not suggestions."

def new_lineage(character_ids, reference_asset_ids, source_panel_id, seed=None, provider="", model="", parent_image_id=None, metadata=None):
    return GenerationLineage(str(uuid4()), character_ids, reference_asset_ids, source_panel_id, seed, provider, model, parent_image_id, metadata or {})
