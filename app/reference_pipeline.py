from __future__ import annotations
from dataclasses import dataclass
from .image_generation import ImageRequest

@dataclass(frozen=True)
class ReferenceSelection:
    character_id: str
    assets: list[dict]
    reason: str

def _value(asset, key, default=""):
    if isinstance(asset, dict): return asset.get(key, default)
    return getattr(asset, key, default)

def _as_dict(asset):
    return {"asset_id":_value(asset,"asset_id",_value(asset,"id")),"character_id":_value(asset,"character_id"),"file_path":_value(asset,"file_path"),"view":_value(asset,"view"),"pose":_value(asset,"pose"),"expression":_value(asset,"expression"),"outfit":_value(asset,"outfit"),"age":_value(asset,"age")}

def select_character_references(character_id: str, assets: list, view: str = "", pose: str = "", expression: str = "", outfit: str = "", limit: int = 3) -> ReferenceSelection:
    canon=[a for a in assets if _value(a,"is_canon",True)]
    def score(a):
        total=0
        for wanted, attr in ((view,"view"),(pose,"pose"),(expression,"expression"),(outfit,"outfit")):
            if wanted and _value(a,attr)==wanted: total+=3
            elif wanted and not _value(a,attr): total+=1
        return total
    ranked=sorted(canon,key=score,reverse=True)
    selected=[_as_dict(a) for a in ranked[:max(1,limit)]]
    return ReferenceSelection(character_id, selected, "ranked canonical assets by panel view/pose/expression/outfit")

def select_panel_references(panel: dict, character_assets: dict[str,list], character_ids: list[str], limit_per_character: int = 2) -> list[dict]:
    view=(panel.get("shot") or "").lower(); pose=(panel.get("action") or "").lower(); expression=(panel.get("expression") or "").lower()
    result=[]
    for character_id in character_ids:
        selection=select_character_references(character_id, character_assets.get(character_id,[]), view=view, pose=pose, expression=expression, limit=limit_per_character)
        result.extend({**asset,"reason":selection.reason} for asset in selection.assets)
    return result

def build_image_request(prompt: str, selections: list[ReferenceSelection], width: int = 1024, height: int = 1024, count: int = 1) -> ImageRequest:
    refs=[]
    for selection in selections: refs.extend({"character_id":selection.character_id,**asset} for asset in selection.assets)
    return ImageRequest(prompt=prompt, reference_assets=refs, width=width, height=height, count=count, metadata={"reference_count":len(refs)})
