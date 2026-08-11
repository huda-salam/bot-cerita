import asyncio
from pathlib import Path

from .config import settings
from .llm import llm
from .models import (
    Character,
    ExpertPanel,
    ExpertReview,
    StoryOutline,
    StorySpec,
    StoryRequest,
    WhatIfResult,
)

PROMPT_ROOT = Path(__file__).parent / "prompts"


def load_prompt(name: str) -> str:
    return (PROMPT_ROOT / f"{name}.md").read_text(encoding="utf-8")


async def generate_what_ifs(request: StoryRequest) -> WhatIfResult:
    if request.what_if_count == 0:
        return WhatIfResult(candidates=[], recommended_index=0)

    system = load_prompt("what_if")
    user = (
        f"USER REQUEST:\n{request.model_dump_json()}\n\n"
        f"Generate exactly {request.what_if_count} candidates."
    )
    return await llm.generate(system, user, WhatIfResult, settings.what_if_model)


async def _review(expert_name: str, prompt_name: str, spec: StorySpec, outline: StoryOutline) -> ExpertReview:
    system = load_prompt(prompt_name)
    user = f"SPEC:\n{spec.model_dump_json()}\nOUTLINE:\n{outline.model_dump_json()}"
    review = await llm.generate(system, user, ExpertReview, settings.expert_model)
    return review.model_copy(update={"expert": expert_name})


async def run_expert_panel(spec: StorySpec, outline: StoryOutline) -> ExpertPanel:
    reviews = await asyncio.gather(
        _review("plot", "expert_plot", spec, outline),
        _review("children_literature", "expert_child", spec, outline),
        _review("character", "expert_character", spec, outline),
    )
    return ExpertPanel(reviews=list(reviews))


def format_expert_guidance(panel: ExpertPanel) -> str:
    sections: list[str] = []
    for review in panel.reviews:
        sections.append(
            "\n".join(
                [
                    f"EXPERT: {review.expert}",
                    f"SCORE: {review.score}",
                    "STRENGTHS:",
                    *[f"- {x}" for x in review.strengths],
                    "RISKS:",
                    *[f"- {x}" for x in review.risks],
                    "RECOMMENDATIONS:",
                    *[f"- {x}" for x in review.recommendations],
                ]
            )
        )
    return "\n\n--- EXPERT REVIEW ---\n\n".join(sections)
