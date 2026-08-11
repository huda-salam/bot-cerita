from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class CostPolicy:
    max_episode_budget_usd: float = 10.0
    max_shot_budget_usd: float = 0.25
    prefer_local: bool = True
    allow_premium_video: bool = False
    premium_shot_score: float = 8.5
    retry_limit: int = 2

@dataclass(frozen=True)
class GenerationDecision:
    mode: str
    provider: str | None
    reason: str
    estimated_cost_usd: float

def choose_generation_mode(*, motion_score: float, visual_importance: float, estimated_cost_usd: float, policy: CostPolicy) -> GenerationDecision:
    if estimated_cost_usd > policy.max_shot_budget_usd:
        return GenerationDecision('static_motion', None, 'shot exceeds per-shot budget', 0.0)
    if policy.allow_premium_video and visual_importance >= policy.premium_shot_score and motion_score >= policy.premium_shot_score:
        return GenerationDecision('ai_video', 'preferred', 'high-value motion shot', estimated_cost_usd)
    if motion_score >= 6:
        return GenerationDecision('light_motion', None, 'motion can be produced with 2D/camera animation', 0.0)
    return GenerationDecision('static_motion', None, 'low motion requirement', 0.0)
