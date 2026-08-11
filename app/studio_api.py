from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .studio_persistence import create_project, get_project, update_project, add_scene, list_scenes, add_panel, get_panel, set_panel_references, list_panel_references
from .project_assets import attach_character, list_project_characters, project_reference_assets

router = APIRouter()
class ProjectCreate(BaseModel): title: str; universe_id: str | None = None
class ProjectUpdate(BaseModel): title: str | None = None; status: str | None = None; style_bible: str | None = None; metadata: dict | None = None
class CharacterAttach(BaseModel): character_id: str
class SceneCreate(BaseModel): scene_number: int; title: str = ""; summary: str = ""
class PanelCreate(BaseModel):
    panel_number: int; purpose: str = ""; shot: str = ""; camera: str = ""; action: str = ""; expression: str = ""; dialogue: str = ""; narration: str = ""; visual_prompt: str = ""
class PanelReference(BaseModel): asset_id: str; character_id: str; reason: str = "manual selection"
class PanelReferencesRequest(BaseModel): references: list[PanelReference]

@router.post("/studio/projects")
async def post_project(request: ProjectCreate): return create_project(request.title, request.universe_id)

@router.get("/studio/projects/{project_id}")
async def get_project_endpoint(project_id: str):
    project=get_project(project_id)
    if not project: raise HTTPException(status_code=404, detail="Project not found")
    project["scenes"]=list_scenes(project_id); project["character_ids"]=list_project_characters(project_id); project["reference_assets"]=project_reference_assets(project_id); return project

@router.patch("/studio/projects/{project_id}")
async def patch_project(project_id: str, request: ProjectUpdate):
    project=update_project(project_id, **request.model_dump(exclude_none=True))
    if not project: raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/studio/projects/{project_id}/characters")
async def post_project_character(project_id: str, request: CharacterAttach):
    if not get_project(project_id): raise HTTPException(status_code=404, detail="Project not found")
    attach_character(project_id, request.character_id); return {"project_id":project_id,"character_ids":list_project_characters(project_id),"reference_assets":project_reference_assets(project_id)}

@router.get("/studio/projects/{project_id}/characters")
async def get_project_characters(project_id: str):
    if not get_project(project_id): raise HTTPException(status_code=404, detail="Project not found")
    return {"character_ids":list_project_characters(project_id),"reference_assets":project_reference_assets(project_id)}

@router.post("/studio/projects/{project_id}/scenes")
async def post_scene(project_id: str, request: SceneCreate):
    if not get_project(project_id): raise HTTPException(status_code=404, detail="Project not found")
    return add_scene(project_id, request.scene_number, request.title, request.summary)

@router.get("/studio/projects/{project_id}/scenes")
async def get_scenes(project_id: str):
    if not get_project(project_id): raise HTTPException(status_code=404, detail="Project not found")
    return list_scenes(project_id)

@router.post("/studio/scenes/{scene_id}/panels")
async def post_panel(scene_id: str, request: PanelCreate): return add_panel(scene_id, request.panel_number, **request.model_dump(exclude={"panel_number"}))

@router.get("/studio/panels/{panel_id}/references")
async def get_panel_references(panel_id: str):
    if not get_panel(panel_id): raise HTTPException(status_code=404, detail="Panel not found")
    return list_panel_references(panel_id)

@router.put("/studio/panels/{panel_id}/references")
async def put_panel_references(panel_id: str, request: PanelReferencesRequest):
    if not get_panel(panel_id): raise HTTPException(status_code=404, detail="Panel not found")
    return set_panel_references(panel_id, [r.model_dump() for r in request.references])
