from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

@dataclass(frozen=True)
class BenchmarkCase:
    id: str
    name: str
    panel_prompts: list[str]
    reference_asset_ids: list[str] = field(default_factory=list)
    requirements: dict[str, bool] = field(default_factory=dict)

@dataclass(frozen=True)
class BenchmarkRun:
    id: str
    case_id: str
    provider: str
    model: str
    results: list[dict[str, Any]] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)
    created_at: str = ""

def create_case(name: str, panel_prompts: list[str], reference_asset_ids: list[str] | None = None, requirements: dict[str, bool] | None = None) -> BenchmarkCase:
    return BenchmarkCase(str(uuid4()), name, panel_prompts, reference_asset_ids or [], requirements or {})

def start_run(case: BenchmarkCase, provider: str, model: str) -> BenchmarkRun:
    return BenchmarkRun(str(uuid4()), case.id, provider, model, created_at=datetime.now(timezone.utc).isoformat())

def score_run(run: BenchmarkRun, scores: dict[str, float]) -> BenchmarkRun:
    normalized = {k: max(0.0, min(10.0, float(v))) for k, v in scores.items()}
    return BenchmarkRun(run.id, run.case_id, run.provider, run.model, run.results, normalized, run.created_at)
