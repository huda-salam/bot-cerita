from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(frozen=True)
class PanelDraft:
    panel_id: str
    description: str
    characters: list[str] = field(default_factory=list)
    dialogue: list[str] = field(default_factory=list)
    visual_focus: str = ''
    shot_type: str = 'medium'

@dataclass(frozen=True)
class PageDraft:
    page_number: int
    purpose: str
    panels: list[PanelDraft]

@dataclass(frozen=True)
class IllustratedStoryDraft:
    title: str
    logline: str
    pages: list[PageDraft]

def plan_from_outline(title: str, logline: str, outline: list[dict], max_pages: int = 3) -> IllustratedStoryDraft:
    if not 1 <= len(outline) <= max_pages:
        raise ValueError(f'outline must contain 1-{max_pages} pages')
    pages=[]
    for page_no, page in enumerate(outline, 1):
        panels=[]
        for idx, raw in enumerate(page.get('panels', []), 1):
            panels.append(PanelDraft(panel_id=f'p{page_no}-{idx}', description=str(raw.get('description','')), characters=list(raw.get('characters',[])), dialogue=list(raw.get('dialogue',[])), visual_focus=str(raw.get('visual_focus','')), shot_type=str(raw.get('shot_type','medium'))))
        if not panels:
            raise ValueError(f'page {page_no} must contain at least one panel')
        pages.append(PageDraft(page_no, str(page.get('purpose','')), panels))
    return IllustratedStoryDraft(title, logline, pages)
