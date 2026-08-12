from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal

@dataclass(frozen=True)
class PanelSpec:
    panel_id: str
    description: str
    characters: list[str] = field(default_factory=list)
    dialogue: list[str] = field(default_factory=list)
    reference_asset_ids: list[str] = field(default_factory=list)
    image_status: Literal['draft', 'approved', 'needs_revision'] = 'draft'

@dataclass(frozen=True)
class PageSpec:
    page_number: int
    panels: list[PanelSpec]
    width: int = 1600
    height: int = 2560

@dataclass(frozen=True)
class IllustratedStorySpec:
    title: str
    pages: list[PageSpec]
    style_bible: str = ''

def validate_story(story: IllustratedStorySpec) -> list[str]:
    errors: list[str] = []
    if not 1 <= len(story.pages) <= 3:
        errors.append('MVP illustrated story must contain 1–3 pages')
    for page in story.pages:
        if not 1 <= len(page.panels) <= 8:
            errors.append(f'page {page.page_number}: expected 1–8 panels')
        for panel in page.panels:
            if not panel.description.strip():
                errors.append(f'panel {panel.panel_id}: missing description')
            if panel.dialogue and not panel.characters:
                errors.append(f'panel {panel.panel_id}: dialogue has no character')
    return errors
