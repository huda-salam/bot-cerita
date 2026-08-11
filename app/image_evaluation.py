from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class EvaluationMetric:
    name: str
    score: float
    method: str
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class ImageEvaluation:
    image_id: str
    metrics: list[EvaluationMetric]
    overall: float
    warnings: list[str] = field(default_factory=list)

def aggregate(metrics: list[EvaluationMetric], weights: dict[str, float] | None = None) -> float:
    if not metrics: return 0.0
    weights=weights or {}; total=sum(max(0.0,weights.get(m.name,1.0)) for m in metrics)
    if total==0: return 0.0
    return sum(max(0.0,min(10.0,m.score))*max(0.0,weights.get(m.name,1.0)) for m in metrics)/total

def evaluate(image_id: str, metrics: list[EvaluationMetric], threshold: float=7.0) -> ImageEvaluation:
    overall=aggregate(metrics); warnings=[f'{m.name} below threshold' for m in metrics if m.score<threshold]
    return ImageEvaluation(image_id=image_id,metrics=metrics,overall=overall,warnings=warnings)
