from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from .image_provider import ImageGenerationRequest, registry
from .image_provider_router import ProviderRequirement, choose_provider
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

class ProviderRouteRequest(BaseModel):
    text_to_image: bool = True
    image_to_image: bool = False
    multi_reference: bool = False
    character_reference: bool = False
    style_reference: bool = False
    inpainting: bool = False
    seed: bool = False
    priorities: dict[str, int] = Field(default_factory=dict)

@router.get('/image-providers')
async def providers(): return {'providers': registry.names()}

@router.post('/image-providers/route')
async def route_provider(request: ProviderRouteRequest):
    requirement = ProviderRequirement(**request.model_dump(exclude={'priorities'}))
    provider = choose_provider(requirement, registry.names(), request.priorities)
    if not provider:
        raise HTTPException(status_code=422, detail='No registered image provider satisfies the requested capabilities')
    return {'provider': provider.name, 'capabilities': provider.capabilities.__dict__, 'priority': provider.priority}

@router.post('/image-providers/generate')
async def generate(request: GenerateRequest):
    try: provider = registry.get(request.provider)
    except KeyError as exc: raise HTTPException(status_code=404, detail=str(exc)) from exc
    context = build_generation_context('adhoc', request.character_ids, request.reference_assets, request.style_bible, request.continuity_notes, request.negative_prompt, request.seed)
    result = await provider.generate(ImageGenerationRequest(prompt=request.prompt, context=context, model=request.model))
    return result.__dict__
