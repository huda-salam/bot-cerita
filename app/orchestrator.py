from dataclasses import dataclass, field
from uuid import uuid4

from .agents import director, planner, writer, critic, rewriter
from .config import settings
from .context import resolve_universe_context
from .expert_layer import generate_what_ifs, run_expert_panel, format_expert_guidance
from .models import StoryRequest, StorySpec, StoryOutline, Story, Critique, StoryBible, WhatIfResult
from .persistence import init_db, save_state


@dataclass
class StoryState:
    id: str
    request: StoryRequest
    universe_context: str = ""
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
            "universe_context": self.universe_context,
            "what_if": self.what_if.model_dump(mode="json") if self.what_if else None,
            "spec": self.spec.model_dump(mode="json") if self.spec else None,
            "outline": self.outline.model_dump(mode="json") if self.outline else None,
            "bible": self.bible.model_dump(mode="json"),
            "story": self.story.model_dump(mode="json") if self.story else None,
            "critique": self.critique.model_dump(mode="json") if self.critique else None,
            "revisions": self.revisions,
        }


def build_initial_bible(spec: StorySpec) -> StoryBible:
    return StoryBible(characters=spec.characters, locations=[spec.setting], rules=[], timeline=[], unresolved_threads=[spec.conflict])


async def run_story(request: StoryRequest) -> StoryState:
    init_db()
    state = StoryState(id=str(uuid4()), request=request)
    state.universe_context = resolve_universe_context(request)
    save_state(state.id, state.snapshot(), "ideation")

    state.what_if = await generate_what_ifs(request)
    save_state(state.id, state.snapshot(), "directing")

    state.spec = await director(request, state.what_if.model_dump_json(), state.universe_context)
    state.spec = state.spec.model_copy(update={"universe_context": state.universe_context})
    state.bible = build_initial_bible(state.spec)
    save_state(state.id, state.snapshot(), "planning", state.spec.title)

    state.outline = await planner(state.spec)
    save_state(state.id, state.snapshot(), "expert_review", state.spec.title)

    panel = await run_expert_panel(state.spec, state.outline)
    guidance = format_expert_guidance(panel)
    state.spec = state.spec.model_copy(update={"expert_guidance": guidance})
    save_state(state.id, state.snapshot(), "writing", state.spec.title)

    state.story = await writer(state.spec, state.outline, state.bible.model_dump_json(), guidance)
    save_state(state.id, state.snapshot(), "reviewing", state.story.title)

    state.bible = refresh_bible_from_story(state.bible, state.story)
    save_state(state.id, state.snapshot(), "reviewing", state.story.title)

    for _ in range(settings.max_revisions + 1):
        state.critique = await critic(state.spec, state.outline, state.story, state.bible.model_dump_json(), guidance)
        save_state(state.id, state.snapshot(), "revising" if state.critique.needs_revision else "completed", state.story.title)
        if not state.critique.needs_revision or state.critique.overall_score >= settings.critic_threshold:
            break
        if state.revisions >= settings.max_revisions:
            break
        state.story = await rewriter(state.spec, state.story, state.critique, state.bible.model_dump_json(), guidance)
        state.bible = refresh_bible_from_story(state.bible, state.story)
        state.revisions += 1
        save_state(state.id, state.snapshot(), "reviewing", state.story.title)

    save_state(state.id, state.snapshot(), "completed", state.story.title if state.story else "")
    return state


def refresh_bible_from_story(bible: StoryBible, story: Story) -> StoryBible:
    timeline = list(bible.timeline)
    for index, scene in enumerate(story.scenes, start=1):
        marker = f"Scene {index}: {scene[:500].replace(chr(10), ' ')}"
        if marker not in timeline:
            timeline.append(marker)
    return StoryBible(characters=bible.characters, locations=bible.locations, rules=bible.rules,
                      timeline=timeline, unresolved_threads=bible.unresolved_threads)
