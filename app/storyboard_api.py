from fastapi import APIRouter
from pydantic import BaseModel, Field
from .storyboard import build_storyboard
from .visual_bible import build_character_visual_profile

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

@router.post("/storyboards")
async def create_storyboard(request: StoryboardRequest):
    characters = [{"id": cid} for cid in request.character_ids]
    profiles = {cid: build_character_visual_profile(cid) for cid in request.character_ids}
    beats = []
    for beat in request.beats:
        data = beat.model_dump()
        ids = data.pop("character_ids")
        data["characters"] = [{"id": cid} for cid in (ids or request.character_ids)]
        beats.append(data)
    board = build_storyboard(request.title, request.scene_number, request.setting, characters, beats, profiles, request.style_bible)
    return {"title": board.title, "scene_number": board.scene_number, "panels": [p.__dict__ for p in board.panels]}
