from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

@dataclass(frozen=True)
class GenerationLineage:
    id: str
    project_id: str | None
    scene_id: str | None
    panel_id: str
    context_id: str | None
    provider: str
    model: str
    prompt: str
    reference_asset_ids: list[str] = field(default_factory=list)
    seed: int | None = None
    parent_generation_id: str | None = None
    revision: int = 1
    status: str = 'created'
    estimated_cost_usd: float = 0.0
    actual_cost_usd: float | None = None
    output_url: str = ''
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = ''

def create_lineage(*, panel_id: str, provider: str, model: str, prompt: str, project_id: str | None = None, scene_id: str | None = None, context_id: str | None = None, reference_asset_ids: list[str] | None = None, seed: int | None = None, parent_generation_id: str | None = None, revision: int = 1, estimated_cost_usd: float = 0.0, metadata: dict[str, Any] | None = None) -> GenerationLineage:
    return GenerationLineage(id=str(uuid4()), project_id=project_id, scene_id=scene_id, panel_id=panel_id, context_id=context_id, provider=provider, model=model, prompt=prompt, reference_asset_ids=reference_asset_ids or [], seed=seed, parent_generation_id=parent_generation_id, revision=revision, estimated_cost_usd=estimated_cost_usd, metadata=metadata or {}, created_at=datetime.now(timezone.utc).isoformat())
