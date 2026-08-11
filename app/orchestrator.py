from dataclasses import dataclass
from .agents import director, planner, writer, critic, rewriter
from .config import settings
from .models import StoryRequest, StorySpec, StoryOutline, Story, Critique

@dataclass
class StoryState:
    request: StoryRequest
    spec: StorySpec | None = None
    outline: StoryOutline | None = None
    story: Story | None = None
    critique: Critique | None = None
    revisions: int = 0

async def run_story(request: StoryRequest) -> StoryState:
    state = StoryState(request=request)
    state.spec = await director(request)
    state.outline = await planner(state.spec)
    state.story = await writer(state.spec, state.outline)

    for _ in range(settings.max_revisions + 1):
        state.critique = await critic(state.spec, state.outline, state.story)
        if not state.critique.needs_revision or state.critique.overall_score >= settings.critic_threshold:
            break
        if state.revisions >= settings.max_revisions:
            break
        state.story = await rewriter(state.spec, state.story, state.critique)
        state.revisions += 1
    return state
