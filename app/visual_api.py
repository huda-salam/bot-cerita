from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .visual_bible import build_character_visual_profile, build_visual_prompt

router = APIRouter()

class VisualPromptRequest(BaseModel):
    scene_description: str
    style_bible: str = ""

@router.get("/characters/{character_id}/visual-profile")
async def visual_profile(character_id: str):
    return build_character_visual_profile(character_id).__dict__

@router.post("/characters/{character_id}/visual-prompt")
async def visual_prompt(character_id: str, request: VisualPromptRequest):
    profile = build_character_visual_profile(character_id)
    return {"prompt": build_visual_prompt(profile, request.scene_description, request.style_bible), "references": profile.references, "anchors": profile.anchors}
