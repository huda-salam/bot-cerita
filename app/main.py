from fastapi import FastAPI, HTTPException
from .models import StoryRequest, StoryResponse, Universe, UniverseCreate, CharacterCreate, CanonEntry, CanonEntryCreate
from .persistence import init_db, create_universe, list_universes, get_universe, create_character, list_characters, create_canon_entry, list_canon_entries
from .asset_api import router as asset_router
from .world_api import router as world_router
from .visual_api import router as visual_router
from .storyboard_api import router as storyboard_router
from .studio_api import router as studio_router
from .image_provider_api import router as image_provider_router
from .benchmark_api import router as benchmark_router
from .character_asset_api import router as character_asset_router
from .reference_selector_api import router as reference_selector_router
from .panel_reference_api import router as panel_reference_router
from .vertical_slice_api import router as vertical_slice_router
from .benchmark_persistence import init_benchmark_db
from .context_engine import build_context_pack
from .studio_persistence import init_studio_tables
from .story_workflow import create_story_from_idea
from pydantic import BaseModel, Field

app=FastAPI(title="Bot Cerita",version="2.9.0")
for router in (asset_router,world_router,visual_router,storyboard_router,studio_router,image_provider_router,benchmark_router,character_asset_router,reference_selector_router,panel_reference_router,vertical_slice_router): app.include_router(router)
class ContextRequest(BaseModel):
    query:str
    character_ids:list[str]=Field(default_factory=list)
    max_items:int=Field(default=40,ge=1,le=200)
@app.on_event("startup")
def startup(): init_db(); init_studio_tables(); init_benchmark_db()
@app.get("/health")
async def health(): return {"status":"ok","version":"2.9.0"}
@app.get("/universes",response_model=list[Universe])
async def get_universes(): return list_universes()
@app.post("/universes",response_model=Universe)
async def post_universe(request:UniverseCreate):
    try:return create_universe(request)
    except Exception as exc:raise HTTPException(status_code=409,detail=str(exc)) from exc
@app.get("/universes/{universe_id}",response_model=Universe)
async def get_universe_endpoint(universe_id:str):
    u=get_universe(universe_id)
    if not u:raise HTTPException(status_code=404,detail="Universe not found")
    return u
@app.get("/universes/{universe_id}/characters")
async def get_characters(universe_id:str):
    if not get_universe(universe_id):raise HTTPException(status_code=404,detail="Universe not found")
    return [{"id":cid,**c.model_dump(mode="json")} for cid,c in list_characters(universe_id)]
@app.post("/universes/{universe_id}/characters")
async def post_character(universe_id:str,request:CharacterCreate):
    result=create_character(universe_id,request)
    if not result:raise HTTPException(status_code=404,detail="Universe not found")
    cid,c=result;return {"id":cid,**c.model_dump(mode="json")}
@app.get("/universes/{universe_id}/canon",response_model=list[CanonEntry])
async def get_canon(universe_id:str):
    if not get_universe(universe_id):raise HTTPException(status_code=404,detail="Universe not found")
    return list_canon_entries(universe_id)
@app.post("/universes/{universe_id}/canon",response_model=CanonEntry)
async def post_canon(universe_id:str,request:CanonEntryCreate):
    e=create_canon_entry(universe_id,request)
    if not e:raise HTTPException(status_code=404,detail="Universe not found")
    return e
@app.post("/universes/{universe_id}/context")
async def resolve_context(universe_id:str,request:ContextRequest):
    try:
        p=build_context_pack(universe_id,request.character_ids,request.query,request.max_items)
        return {"context":p.as_text(),"warnings":p.warnings,"counts":{"characters":len(p.characters),"canon":len(p.canon),"entities":len(p.world_entities),"relationships":len(p.relationships),"timeline":len(p.timeline)}}
    except ValueError as exc:raise HTTPException(status_code=404,detail=str(exc)) from exc
@app.post("/stories",response_model=StoryResponse)
async def create_story(request:StoryRequest):
    try:
        r=await create_story_from_idea(request);return StoryResponse(id=r.story_id,title=r.title,story=r.story,score=r.score,revisions=r.revisions)
    except ValueError as exc:raise HTTPException(status_code=404,detail=str(exc)) from exc
    except Exception as exc:raise HTTPException(status_code=502,detail=str(exc)) from exc
