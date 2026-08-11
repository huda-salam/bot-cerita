from fastapi import APIRouter, HTTPException
from .asset_registry import register_character_asset, list_character_assets
from .persistence import list_characters, get_universe

router = APIRouter(prefix="/characters", tags=["character-assets"])


def _exists(character_id: str) -> bool:
    for cid, _ in list_characters_for_all_universes():
        if cid == character_id:
            return True
    return False


def list_characters_for_all_universes():
    # MVP helper: character IDs are globally unique UUIDs.
    from .persistence import list_universes
    for universe in list_universes():
        yield from list_characters(universe.id)


@router.get("/{character_id}/assets")
async def get_assets(character_id: str):
    if not _exists(character_id):
        raise HTTPException(status_code=404, detail="Character not found")
    return [asset.__dict__ for asset in list_character_assets(character_id)]


@router.post("/{character_id}/assets")
async def post_asset(character_id: str, payload: dict):
    if not _exists(character_id):
        raise HTTPException(status_code=404, detail="Character not found")
    if not payload.get("file_path"):
        raise HTTPException(status_code=422, detail="file_path is required")
    asset = register_character_asset(
        character_id=character_id,
        file_path=payload["file_path"],
        asset_type=payload.get("asset_type", "visual_reference"),
        view=payload.get("view", ""), pose=payload.get("pose", ""),
        expression=payload.get("expression", ""), outfit=payload.get("outfit", ""),
        age=payload.get("age", ""), is_canon=payload.get("is_canon", True),
        source=payload.get("source", "user_provided"),
    )
    return asset.__dict__
