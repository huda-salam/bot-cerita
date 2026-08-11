from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .persistence import get_universe
from .world_model import create_entity, list_entities, create_relationship, list_relationships, create_timeline_event, list_timeline_events

router = APIRouter()

class EntityCreate(BaseModel):
    entity_type: str
    name: str
    description: str = ""
    canon_status: str = "established"

class RelationshipCreate(BaseModel):
    source_id: str
    target_id: str
    relation: str
    description: str = ""
    valid_from: str | None = None
    valid_until: str | None = None

class TimelineEventCreate(BaseModel):
    title: str
    event_date: str | None = None
    description: str = ""
    canon_status: str = "established"


def ensure_universe(universe_id: str):
    if not get_universe(universe_id):
        raise HTTPException(status_code=404, detail="Universe not found")

@router.get("/universes/{universe_id}/world/entities")
async def get_world_entities(universe_id: str, entity_type: str | None = None):
    ensure_universe(universe_id)
    return [e.__dict__ for e in list_entities(universe_id, entity_type)]

@router.post("/universes/{universe_id}/world/entities")
async def post_world_entity(universe_id: str, request: EntityCreate):
    ensure_universe(universe_id)
    return create_entity(universe_id, request.entity_type, request.name, request.description, request.canon_status).__dict__

@router.get("/universes/{universe_id}/world/relationships")
async def get_relationships(universe_id: str, entity_id: str | None = None):
    ensure_universe(universe_id)
    return list_relationships(universe_id, entity_id)

@router.post("/universes/{universe_id}/world/relationships")
async def post_relationship(universe_id: str, request: RelationshipCreate):
    ensure_universe(universe_id)
    return create_relationship(universe_id, **request.model_dump())

@router.get("/universes/{universe_id}/world/timeline")
async def get_timeline(universe_id: str):
    ensure_universe(universe_id)
    return list_timeline_events(universe_id)

@router.post("/universes/{universe_id}/world/timeline")
async def post_timeline(universe_id: str, request: TimelineEventCreate):
    ensure_universe(universe_id)
    return create_timeline_event(universe_id, **request.model_dump())
