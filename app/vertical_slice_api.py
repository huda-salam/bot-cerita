from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from .models import StoryRequest
from .studio_persistence import get_project
from .vertical_slice import run_vertical_slice

router=APIRouter()
class VerticalSliceRequest(BaseModel):
    idea: str
    universe_id: str | None = None
    character_ids: list[str] = Field(default_factory=list)
    target_age: str = '7-10'
    genre: str = 'fantasy'
    tone: list[str] = Field(default_factory=lambda: ['warm','funny','adventurous'])
    language: str = 'Indonesian'
    length: str = 'short'
    panels_per_scene: int = Field(default=3, ge=1, le=8)
    generate_images: bool = False

@router.post('/studio/projects/{project_id}/vertical-slice')
async def vertical_slice(project_id: str, request: VerticalSliceRequest):
    if not get_project(project_id):
        raise HTTPException(status_code=404, detail='Project not found')
    story_request=StoryRequest(**request.model_dump(exclude={'panels_per_scene','generate_images'}))
    try:
        result=await run_vertical_slice(story_request,project_id,request.panels_per_scene,request.generate_images)
        return result.__dict__
    except Exception as exc:
        raise HTTPException(status_code=502,detail=str(exc)) from exc
