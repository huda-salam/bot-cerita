from fastapi import APIRouter
from pydantic import BaseModel, Field
from .character_assets import asset_registry
from .panel_references import resolve_panel_references

router=APIRouter()
class PanelReferenceRequest(BaseModel):
    character_id: str
    view: str=''; pose: str=''; expression: str=''; outfit: str=''; age: str=''; limit: int=Field(default=3,ge=1,le=10)

@router.post('/studio/panels/{panel_id}/references')
async def resolve_references(panel_id: str, request: PanelReferenceRequest):
    assets=[a.__dict__ for a in asset_registry.list(request.character_id)]
    result=resolve_panel_references(panel_id,request.character_id,assets,request.model_dump(exclude={'character_id','limit'}),request.limit)
    return {'panel_id':result.panel_id,'character_id':result.character_id,'requested':result.requested,'selected_assets':result.selected_assets,'candidates':result.candidates}
