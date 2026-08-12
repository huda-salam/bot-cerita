from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .character_assets import asset_registry

router=APIRouter()
class AssetCreate(BaseModel):
    file_path: str
    asset_type: str='reference'
    is_canon: bool=True
    view: str=''
    pose: str=''
    expression: str=''
    outfit: str=''
    age: str=''
    notes: str=''

@router.post('/characters/{character_id}/assets')
async def add_character_asset(character_id: str, request: AssetCreate):
    return asset_registry.add(character_id, **request.model_dump()).__dict__

@router.get('/characters/{character_id}/assets')
async def list_character_assets(character_id: str):
    return [a.__dict__ for a in asset_registry.list(character_id)]

@router.get('/character-assets/{asset_id}')
async def get_character_asset(asset_id: str):
    try: return asset_registry.as_dict(asset_id)
    except KeyError: raise HTTPException(status_code=404, detail='Asset not found')
