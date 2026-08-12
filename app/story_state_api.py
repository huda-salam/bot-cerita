from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .models import StoryRequest
from .orchestrator import run_story

router = APIRouter()

class StoryRunRequest(StoryRequest):
    pass

@router.post('/stories/full')
async def create_full_story(request: StoryRunRequest):
    try:
        state = await run_story(request)
        return state.snapshot()
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
