from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .story_studio import studio

router = APIRouter()

class ProjectCreate(BaseModel):
    title: str
    universe_id: str | None = None

class ProjectUpdate(BaseModel):
    status: str | None = None
    scenes: list[dict] | None = None
    selected_characters: list[str] | None = None
    style_bible: str | None = None

@router.post("/studio/projects")
async def create_project(request: ProjectCreate):
    return studio.create(request.title, request.universe_id).__dict__

@router.get("/studio/projects/{project_id}")
async def get_project(project_id: str):
    project = studio.get(project_id)
    if not project: raise HTTPException(status_code=404, detail="Project not found")
    return project.__dict__

@router.patch("/studio/projects/{project_id}")
async def update_project(project_id: str, request: ProjectUpdate):
    if not studio.get(project_id): raise HTTPException(status_code=404, detail="Project not found")
    return studio.update(project_id, **request.model_dump(exclude_none=True)).__dict__
