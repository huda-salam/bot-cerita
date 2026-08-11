from fastapi import FastAPI, HTTPException
from .models import StoryRequest, StoryResponse, Universe, UniverseCreate, CharacterCreate, CanonEntry, CanonEntryCreate
from .orchestrator import run_story
from .persistence import init_db, create_universe, list_universes, get_universe, create_character, list_characters, create_canon_entry, list_canon_entries
from .asset_api import router as asset_router
from .world_api import router as world_router
from .visual_api import router as visual_router
from .storyboard_api import router as storyboard_router
from .studio_api import router as studio_router
from .context_engine import build_context_pack
from pydantic import BaseModel, Field

app = FastAPI(title="Bot Cerita", version="1.5.0")
app.include_router(asset_router)
app.include_router(world_router)
app.include_router(visual_router)
app.include_router(storyboard_router)
app.include_router(studio_router)

class ContextRequest(BaseModel):
    query: str
    character_ids: list[str] = Field(default_factory=list)
    max_items: int = Field(default=40, ge=1, le=200)

@app.on_event("startup")
def startup() -> None: init_db()

@app.get("/health")
async def health(): return {"status": "ok", "version": "1.5.0"}

@app.get("/universes", response_model=list[Universe])
async def get_universes(): return list_universes()

@app.post("/universes", response_model=Universe)
async def post_universe(request: UniverseCreate):
    try: return create_universe(request)
    except Exception as exc: raise HTTPException(status_code=409, detail=str(exc)) from exc

@app.get("/universes/{universe_id}", response_model=Universe)
async def get_universe_endpoint(universe_id: str):
    universe = get_universe(universe_id)
    if not universe: raise HTTPException(status_code=404, detail="Universe not found")
    return universe

@app.get("/universes/{universe_id}/characters")
async def get_characters(universe_id: str):
    if not get_universe(universe_id): raise HTTPException(status_code=404, detail="Universe not found")
    return [{"id": cid, **character.model_dump(mode="json")} for cid, character in list_characters(universe_id)]

@app.post("/universes/{universe_id}/characters")
async def post_character(universe_id: str, request: CharacterCreate):
    result = create_character(universe_id, request)
    if not result: raise HTTPException(status_code=404, detail="Universe not found")
    character_id, character = result
    return {"id": character_id, **character.model_dump(mode="json")}

@app.get("/universes/{universe_id}/canon", response_model=list[CanonEntry])
async def get_canon(universe_id: str):
    if not get_universe(universe_id): raise HTTPException(status_code=404, detail="Universe not found")
    return list_canon_entries(universe_id)

@app.post("/universes/{universe_id}/canon", response_model=CanonEntry)
async def post_canon(universe_id: str, request: CanonEntryCreate):
    entry = create_canon_entry(universe_id, request)
    if not entry: raise HTTPException(status_code=404, detail="Universe not found")
    return entry

@app.post("/universes/{universe_id}/context")
async def resolve_context(universe_id: str, request: ContextRequest):
    try:
        pack = build_context_pack(universe_id, request.character_ids, request.query, request.max_items)
        return {"context": pack.as_text(), "warnings": pack.warnings, "counts": {"characters": len(pack.characters), "canon": len(pack.canon), "entities": len(pack.world_entities), "relationships": len(pack.relationships), "timeline": len(pack.timeline)}}
    except ValueError as exc: raise HTTPException(status_code=404, detail=str(exc)) from exc

@app.post("/stories", response_model=StoryResponse)
async def create_story(request: StoryRequest):
    try:
        state = await run_story(request)
        text = "\n\n".join(state.story.scenes)
        return StoryResponse(id=state.id, title=state.story.title, story=text, score=state.critique.overall_score if state.critique else 0, revisions=state.revisions)
    except ValueError as exc: raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc: raise HTTPException(status_code=502, detail=str(exc)) from exc
