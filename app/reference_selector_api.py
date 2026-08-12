from fastapi import APIRouter
from pydantic import BaseModel, Field
from .character_assets import asset_registry
from .reference_selector import select_references

router=APIRouter()
class ReferenceRequest(BaseModel):
    view: str=''; pose: str=''; expression: str=''; outfit: str=''; age: str=''; limit: int=Field(default=3,ge=1,le=10)

@router.post('/characters/{character_id}/reference-selection')
async def reference_selection(character_id: str, request: ReferenceRequest):
    assets=[a.__dict__ for a in asset_registry.list(character_id)]
    result=select_references(character_id,assets,request.model_dump(),request.limit)
    return {'character_id':result.character_id,'selected':result.selected,'candidates':[{'asset':c.asset,'score':c.score,'reasons':c.reasons} for c in result.candidates]}
