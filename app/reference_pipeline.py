from __future__ import annotations
from dataclasses import dataclass
from .image_generation import ImageRequest

@dataclass(frozen=True)
class ReferenceSelection:
    character_id: str
    assets: list[dict]
    reason: str

def select_character_references(character_id: str, assets: list, view: str = "", pose: str = "") -> ReferenceSelection:
    selected = []
    for asset in assets:
        if not getattr(asset, "is_canon", False):
            continue
        if view and getattr(asset, "view", "") not in {view, ""}:
            continue
        if pose and getattr(asset, "pose", "") not in {pose, ""}:
            continue
        selected.append({"file_path": asset.file_path, "view": asset.view, "pose": asset.pose, "expression": asset.expression, "outfit": asset.outfit, "age": asset.age})
    if not selected:
        selected = [{"file_path": asset.file_path, "view": asset.view, "pose": asset.pose, "expression": asset.expression, "outfit": asset.outfit, "age": asset.age} for asset in assets if getattr(asset, "is_canon", False)]
    return ReferenceSelection(character_id, selected, "canon assets matching requested shot; fallback to all canon assets")

def build_image_request(prompt: str, selections: list[ReferenceSelection], width: int = 1024, height: int = 1024, count: int = 1) -> ImageRequest:
    refs = []
    for selection in selections:
        for asset in selection.assets:
            refs.append({"character_id": selection.character_id, **asset})
    return ImageRequest(prompt=prompt, reference_assets=refs, width=width, height=height, count=count, metadata={"reference_count": len(refs)})
