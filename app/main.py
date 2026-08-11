from fastapi import FastAPI, HTTPException
from .models import StoryRequest, StoryResponse
from .orchestrator import run_story
from .persistence import init_db

app = FastAPI(title="Bot Cerita", version="0.2.0")


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
async def health():
    return {"status": "ok"}


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
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
