from __future__ import annotations
from dataclasses import dataclass
from .models import StoryRequest
from .orchestrator import run_story

@dataclass(frozen=True)
class WorkflowResult:
    story_id: str
    title: str
    story: str
    score: int
    revisions: int

async def create_story_from_idea(request: StoryRequest) -> WorkflowResult:
    state = await run_story(request)
    return WorkflowResult(state.id, state.story.title, "\n\n".join(state.story.scenes), state.critique.overall_score if state.critique else 0, state.revisions)
