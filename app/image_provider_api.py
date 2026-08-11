from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from .image_provider import ImageGenerationRequest, registry
from .visual_context import build_generation_context

router = APIRouter()

class GenerateRequest(BaseModel):
    provider: str = "mock"
    model: str | None = None
    prompt: str = ""
    character_ids: list[str] = Field(default_factory=list)
    reference_assets: list[dict] = Field(default_factory=list)
    style_bible: str = ""
    continuity_notes: list[str] = Field(default_factory=list)
    negative_prompt: str = ""
    seed: int | None = None

@router.get('/image-providers')
async def providers(): return {'providers': registry.names()}

@router.post('/image-providers/generate')
async def generate(request: GenerateRequest):
    try: provider = registry.get(request.provider)
    except KeyError as exc: raise HTTPException(status_code=404, detail=str(exc)) from exc
    context = build_generation_context('adhoc', request.character_ids, request.reference_assets, request.style_bible, request.continuity_notes, request.negative_prompt, request.seed)
    result = await provider.generate(ImageGenerationRequest(prompt=request.prompt, context=context, model=request.model))
    return result.__dict__
