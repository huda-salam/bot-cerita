from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from .storyboard import build_storyboard
from .visual_bible import build_character_visual_profile
from .storyboard_workflow import outline_to_storyboard
from .models import StoryOutline, Scene
from .studio_persistence import get_project, list_scenes

router = APIRouter()

class Beat(BaseModel):
    purpose: str = "advance story"
    shot: str = "medium"
    camera: str = "eye level"
    action: str
    expression: str = "neutral"
    dialogue: str = ""
    narration: str = ""
    character_ids: list[str] = Field(default_factory=list)

class StoryboardRequest(BaseModel):
    title: str
    scene_number: int = 1
    setting: str
    character_ids: list[str] = Field(default_factory=list)
    beats: list[Beat]
    style_bible: str = ""

class ProjectStoryboardRequest(BaseModel):
    title: str
    scenes: list[Scene]
    panels_per_scene: int = Field(default=4, ge=1, le=12)

@router.post("/storyboards")
async def create_storyboard(request: StoryboardRequest):
    characters = [{"id": cid} for cid in request.character_ids]
    profiles = {cid: build_character_visual_profile(cid) for cid in request.character_ids}
    beats = []
    for beat in request.beats:
        data = beat.model_dump(); ids = data.pop("character_ids")
        data["characters"] = [{"id": cid} for cid in (ids or request.character_ids)]
        beats.append(data)
    board = build_storyboard(request.title, request.scene_number, request.setting, characters, beats, profiles, request.style_bible)
    return {"title": board.title, "scene_number": board.scene_number, "panels": [p.__dict__ for p in board.panels]}

@router.post('/studio/projects/{project_id}/storyboard')
async def create_project_storyboard(project_id: str, request: ProjectStoryboardRequest):
    if not get_project(project_id): raise HTTPException(status_code=404, detail='Project not found')
    result=outline_to_storyboard(project_id, StoryOutline(title=request.title, scenes=request.scenes), request.panels_per_scene)
    return {'title':request.title,'scenes':result.scenes,'panels':result.panels}

@router.get('/studio/projects/{project_id}/storyboard')
async def get_project_storyboard(project_id: str):
    if not get_project(project_id): raise HTTPException(status_code=404, detail='Project not found')
    return {'scenes':list_scenes(project_id)}
