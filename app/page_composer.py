from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class PanelPlacement:
    panel_id: str
    x: float
    y: float
    width: float
    height: float
    z_index: int = 0

@dataclass(frozen=True)
class PageCanvas:
    width: int = 1600
    height: int = 2400
    background: str = '#ffffff'

@dataclass(frozen=True)
class PageComposition:
    page_number: int
    canvas: PageCanvas
    panels: list[PanelPlacement] = field(default_factory=list)
    text_blocks: list[dict[str, Any]] = field(default_factory=list)

LAYOUTS: dict[str, list[tuple[float, float, float, float]]] = {
    'two_by_two': [(0,0,.5,.5),(.5,0,.5,.5),(0,.5,.5,.5),(.5,.5,.5,.5)],
    'three_vertical': [(0,0,1,.3333),(0,.3333,1,.3333),(0,.6666,1,.3334)],
    'hero_bottom': [(0,0,1,.65),(0,.65,.5,.35),(.5,.65,.5,.35)],
}

def compose_page(page_number: int, panel_ids: list[str], layout: str = 'two_by_two', canvas: PageCanvas | None = None) -> PageComposition:
    if layout not in LAYOUTS:
        raise ValueError(f'Unknown page layout: {layout}')
    slots = LAYOUTS[layout]
    if len(panel_ids) > len(slots):
        raise ValueError(f'Layout {layout} supports at most {len(slots)} panels')
    placements = [PanelPlacement(pid, *slots[i], z_index=i) for i, pid in enumerate(panel_ids)]
    return PageComposition(page_number, canvas or PageCanvas(), placements)
