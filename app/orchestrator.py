from dataclasses import dataclass, field
from uuid import uuid4
from .agents import director, planner, writer, critic, rewriter
from .config import settings
from .models import StoryRequest, StorySpec, StoryOutline, Story, Critique, StoryBible
from .persistence import init_db, save_state


@dataclass
class StoryState:
    id: str
    request: StoryRequest
    spec: StorySpec | None = None
    outline: StoryOutline | None = None
    bible: StoryBible = field(default_factory=StoryBible)
    story: Story | None = None
    critique: Critique | None = None
    revisions: int = 0

    def snapshot(self) -> dict:
        return {
            "id": self.id,
            "request": self.request.model_dump(mode="json"),
            "spec": self.spec.model_dump(mode="json") if self.spec else None,
            "outline": self.outline.model_dump(mode="json") if self.outline else None,
            "bible": self.bible.model_dump(mode="json"),
            "story": self.story.model_dump(mode="json") if self.story else None,
            "critique": self.critique.model_dump(mode="json") if self.critique else None,
            "revisions": self.revisions,
        }


def build_initial_bible(spec: StorySpec) -> StoryBible:
    return StoryBible(
        characters=spec.characters,
        locations=[spec.setting],
        rules=[],
        timeline=[],
        unresolved_threads=[spec.conflict],
    )


async def run_story(request: StoryRequest) -> StoryState:
    init_db()
    state = StoryState(id=str(uuid4()), request=request)
    save_state(state.id, state.snapshot(), "directing")

    state.spec = await director(request)
    state.bible = build_initial_bible(state.spec)
    save_state(state.id, state.snapshot(), "planning", state.spec.title)

    state.outline = await planner(state.spec)
    save_state(state.id, state.snapshot(), "writing", state.spec.title)

    state.story = await writer(state.spec, state.outline, state.bible.model_dump_json())
    save_state(state.id, state.snapshot(), "reviewing", state.story.title)

    for _ in range(settings.max_revisions + 1):
        state.critique = await critic(
            state.spec, state.outline, state.story, state.bible.model_dump_json()
        )
        save_state(state.id, state.snapshot(), "revising" if state.critique.needs_revision else "completed", state.story.title)
        if not state.critique.needs_revision or state.critique.overall_score >= settings.critic_threshold:
            break
        if state.revisions >= settings.max_revisions:
            break
        state.story = await rewriter(
            state.spec, state.story, state.critique, state.bible.model_dump_json()
        )
        state.revisions += 1
        save_state(state.id, state.snapshot(), "reviewing", state.story.title)

    save_state(state.id, state.snapshot(), "completed", state.story.title if state.story else "")
    return state
