from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

@dataclass
class CharacterAsset:
    id: str
    character_id: str
    file_path: str
    asset_type: str = "reference"
    is_canon: bool = True
    view: str = ""
    pose: str = ""
    expression: str = ""
    outfit: str = ""
    age: str = ""
    notes: str = ""
    created_at: str = ""

class CharacterAssetRegistry:
    def __init__(self): self._assets: dict[str, CharacterAsset] = {}
    def add(self, character_id: str, file_path: str, **kwargs: Any) -> CharacterAsset:
        asset=CharacterAsset(str(uuid4()), character_id, file_path, created_at=datetime.now(timezone.utc).isoformat(), **kwargs); self._assets[asset.id]=asset; return asset
    def list(self, character_id: str) -> list[CharacterAsset]: return [a for a in self._assets.values() if a.character_id == character_id]
    def get(self, asset_id: str) -> CharacterAsset | None: return self._assets.get(asset_id)
    def as_dict(self, asset_id: str) -> dict[str, Any]:
        asset=self.get(asset_id)
        if not asset: raise KeyError(asset_id)
        return asdict(asset)

asset_registry=CharacterAssetRegistry()
