from fastapi import FastAPI, HTTPException
from .models import StoryRequest, StoryResponse, Universe, UniverseCreate, CharacterCreate, CanonEntry, CanonEntryCreate
from .orchestrator import run_story
from .persistence import (
    init_db, create_universe, list_universes, get_universe,
    create_character, list_characters, create_canon_entry, list_canon_entries,
)

app = FastAPI(title="Bot Cerita", version="0.5.0")


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.5.0"}


@app.get("/universes", response_model=list[Universe])
async def get_universes():
    return list_universes()


@app.post("/universes", response_model=Universe)
async def post_universe(request: UniverseCreate):
    try:
        return create_universe(request)
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/universes/{universe_id}", response_model=Universe)
async def get_universe_endpoint(universe_id: str):
    universe = get_universe(universe_id)
    if not universe:
        raise HTTPException(status_code=404, detail="Universe not found")
    return universe


@app.get("/universes/{universe_id}/characters")
async def get_characters(universe_id: str):
    if not get_universe(universe_id):
        raise HTTPException(status_code=404, detail="Universe not found")
    return [{"id": cid, **character.model_dump(mode="json")} for cid, character in list_characters(universe_id)]


@app.post("/universes/{universe_id}/characters")
async def post_character(universe_id: str, request: CharacterCreate):
    result = create_character(universe_id, request)
    if not result:
        raise HTTPException(status_code=404, detail="Universe not found")
    character_id, character = result
    return {"id": character_id, **character.model_dump(mode="json")}


@app.get("/universes/{universe_id}/canon", response_model=list[CanonEntry])
async def get_canon(universe_id: str):
    if not get_universe(universe_id):
        raise HTTPException(status_code=404, detail="Universe not found")
    return list_canon_entries(universe_id)


@app.post("/universes/{universe_id}/canon", response_model=CanonEntry)
async def post_canon(universe_id: str, request: CanonEntryCreate):
    entry = create_canon_entry(universe_id, request)
    if not entry:
        raise HTTPException(status_code=404, detail="Universe not found")
    return entry


@app.post("/stories", response_model=StoryResponse)
async def create_story(request: StoryRequest):
    try:
        state = await run_story(request)
        text = "\n\n".join(state.story.scenes)
        return StoryResponse(
            id=state.id,
            title=state.story.title,
            story=text,
            score=state.critique.overall_score if state.critique else 0,
            revisions=state.revisions,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
