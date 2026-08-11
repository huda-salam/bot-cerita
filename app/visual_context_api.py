from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from .studio_persistence import get_panel, get_project, list_panel_references
from .project_assets import list_project_characters
from .visual_context import build_generation_context

router = APIRouter()

class GenerationContextRequest(BaseModel):
    continuity_notes: list[str] = Field(default_factory=list)
    negative_prompt: str = ""
    seed: int | None = None
    parent_image_id: str | None = None

@router.post('/studio/panels/{panel_id}/generation-context')
async def create_generation_context(panel_id: str, request: GenerationContextRequest):
    panel = get_panel(panel_id)
    if not panel:
        raise HTTPException(status_code=404, detail='Panel not found')
    refs = list_panel_references(panel_id)
    character_ids = list_project_characters(_project_id_for_panel(panel_id))
    project = get_project(_project_id_for_panel(panel_id))
    context = build_generation_context(panel_id, character_ids, refs, project.get('style_bible','') if project else '', request.continuity_notes, request.negative_prompt, request.seed, request.parent_image_id)
    return {'id': context.id, 'panel_id': context.panel_id, 'character_ids': context.character_ids, 'reference_assets': context.reference_assets, 'style_bible': context.style_bible, 'continuity_notes': context.continuity_notes, 'negative_prompt': context.negative_prompt, 'seed': context.seed, 'parent_image_id': context.parent_image_id, 'prompt_context': context.prompt_context()}

def _project_id_for_panel(panel_id: str) -> str:
    from .studio_persistence import get_scene_project_id
    return get_scene_project_id(get_panel(panel_id)['scene_id'])
