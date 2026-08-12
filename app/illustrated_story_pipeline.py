from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

@dataclass(frozen=True)
class PanelPlan:
    id: str
    page: int
    order: int
    description: str
    characters: list[str] = field(default_factory=list)
    dialogue: list[dict[str, str]] = field(default_factory=list)
    reference_asset_ids: list[str] = field(default_factory=list)
    image_status: str = 'planned'

@dataclass(frozen=True)
class PagePlan:
    page: int
    panels: list[PanelPlan]

@dataclass(frozen=True)
class IllustratedStoryPlan:
    id: str
    title: str
    pages: list[PagePlan]
    max_pages: int = 3
    format: str = 'illustrated-story'

def create_plan(title: str, pages: list[list[dict[str, Any]]]) -> IllustratedStoryPlan:
    if not 1 <= len(pages) <= 3:
        raise ValueError('MVP illustrated stories must contain 1-3 pages')
    page_plans=[]
    for page_no, raw_panels in enumerate(pages, 1):
        panels=[]
        for order, raw in enumerate(raw_panels, 1):
            panels.append(PanelPlan(id=str(uuid4()), page=page_no, order=order, description=str(raw.get('description','')), characters=list(raw.get('characters',[])), dialogue=list(raw.get('dialogue',[])), reference_asset_ids=list(raw.get('reference_asset_ids',[]))))
        page_plans.append(PagePlan(page_no, panels))
    return IllustratedStoryPlan(str(uuid4()), title, page_plans)

def pipeline_status(plan: IllustratedStoryPlan) -> dict[str, Any]:
    panels=[p for page in plan.pages for p in page.panels]
    return {'story_id': plan.id, 'pages': len(plan.pages), 'panels': len(panels), 'panel_status': {p.id:p.image_status for p in panels}, 'next_step': 'generate_panels'}
