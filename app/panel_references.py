from __future__ import annotations
from dataclasses import dataclass
from .reference_selector import select_references

@dataclass(frozen=True)
class PanelReferenceResult:
    panel_id: str
    character_id: str
    requested: dict
    selected_assets: list[dict]
    candidates: list[dict]

def resolve_panel_references(panel_id: str, character_id: str, assets: list[dict], requested: dict, limit: int = 3) -> PanelReferenceResult:
    result=select_references(character_id,assets,requested,limit)
    candidates=[{"asset":c.asset,"score":c.score,"reasons":c.reasons} for c in result.candidates]
    return PanelReferenceResult(panel_id,character_id,requested,result.selected,candidates)
