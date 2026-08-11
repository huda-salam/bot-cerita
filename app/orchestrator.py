from dataclasses import dataclass, field
from uuid import uuid4

from .agents import director, planner, writer, critic, rewriter
from .config import settings
from .expert_layer import generate_what_ifs, run_expert_panel, format_expert_guidance
from .models import (
    StoryRequest,
    StorySpec,
    StoryOutline,
    Story,
    Critique,
    StoryBible,
    WhatIfResult,
)
from .persistence import init_db, save_state


@dataclass
class StoryState:
    id: str
    request: StoryRequest
    what_if: WhatIfResult | None = None
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
            "what_if": self.what_if.model_dump(mode="json") if self.what_if else None,
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
    save_state(state.id, state.snapshot(), "ideation")

    # 1. Explore multiple dramatically different directions before committing.
    state.what_if = await generate_what_ifs(request)
    save_state(state.id, state.snapshot(), "directing")

    what_if_context = state.what_if.model_dump_json() if state.what_if else ""
    state.spec = await director(request, what_if_context)
    state.bible = build_initial_bible(state.spec)
    save_state(state.id, state.snapshot(), "planning", state.spec.title)

    # 2. Build the plot architecture.
    state.outline = await planner(state.spec)
    save_state(state.id, state.snapshot(), "expert_review", state.spec.title)

    # 3. Independent expert panel reviews the architecture before prose is generated.
    panel = await run_expert_panel(state.spec, state.outline)
    guidance = format_expert_guidance(panel)
    state.spec = state.spec.model_copy(update={"expert_guidance": guidance})
    save_state(state.id, state.snapshot(), "writing", state.spec.title)

    # 4. Write with shared Story Bible + expert guidance.
    state.story = await writer(
        state.spec,
        state.outline,
        state.bible.model_dump_json(),
        guidance,
    )
    save_state(state.id, state.snapshot(), "reviewing", state.story.title)

    # 5. Editorial loop.
    for _ in range(settings.max_revisions + 1):
        state.critique = await critic(
            state.spec,
            state.outline,
            state.story,
            state.bible.model_dump_json(),
            guidance,
        )
        save_state(
            state.id,
            state.snapshot(),
            "revising" if state.critique.needs_revision else "completed",
            state.story.title,
        )
        if not state.critique.needs_revision or state.critique.overall_score >= settings.critic_threshold:
            break
        if state.revisions >= settings.max_revisions:
            break

        state.story = await rewriter(
            state.spec,
            state.story,
            state.critique,
            state.bible.model_dump_json(),
            guidance,
        )
        state.revisions += 1
        save_state(state.id, state.snapshot(), "reviewing", state.story.title)

    save_state(state.id, state.snapshot(), "completed", state.story.title if state.story else "")
    return state
