from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from .image_provider import registry
from .image_provider_router import ProviderRequirement, choose_provider

router = APIRouter()

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
async def list_image_providers():
    return {'providers': [{'name': name} for name in registry.names()]}

@router.post('/image-providers/route')
async def route_image_provider(request: ProviderRouteRequest):
    requirement = ProviderRequirement(**request.model_dump(exclude={'priorities'}))
    provider = choose_provider(requirement, registry.names(), request.priorities)
    if not provider:
        raise HTTPException(status_code=422, detail='No registered image provider satisfies the requested capabilities')
    return {'provider': provider.name, 'capabilities': provider.capabilities.__dict__, 'priority': provider.priority}
