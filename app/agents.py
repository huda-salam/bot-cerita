from pathlib import Path
from .config import settings
from .llm import llm
from .models import StoryRequest, StorySpec, StoryOutline, Story, Critique
from .skills import build_skill_context

PROMPT_ROOT = Path(__file__).parent / "prompts"


def prompt(name: str) -> str:
    return (PROMPT_ROOT / f"{name}.md").read_text(encoding="utf-8")


CHILDREN_SKILLS = build_skill_context("children_literature", "dialogue")
PLOT_SKILLS = build_skill_context("plot")


async def director(req: StoryRequest, what_if_context: str = ""):
    system = prompt("director") + "\n\nSPECIALIST SKILLS:\n" + CHILDREN_SKILLS
    user = f"REQUEST:\n{req.model_dump_json()}\n\nWHAT-IF OPTIONS:\n{what_if_context}"
    return await llm.generate(system, user, StorySpec, settings.director_model)


async def planner(spec: StorySpec):
    system = prompt("planner") + "\n\nSPECIALIST SKILLS:\n" + PLOT_SKILLS + "\n" + CHILDREN_SKILLS
    return await llm.generate(system, spec.model_dump_json(), StoryOutline, settings.planner_model)


async def writer(spec: StorySpec, outline: StoryOutline, bible: str = "", expert_guidance: str = ""):
    system = prompt("writer") + "\n\nSPECIALIST SKILLS:\n" + CHILDREN_SKILLS + "\n" + PLOT_SKILLS
    user = (
        f"SPEC:\n{spec.model_dump_json()}\nOUTLINE:\n{outline.model_dump_json()}\n"
        f"STORY BIBLE:\n{bible}\nEXPERT GUIDANCE:\n{expert_guidance}"
    )
    return await llm.generate(system, user, Story, settings.writer_model)


async def critic(spec: StorySpec, outline: StoryOutline, story: Story, bible: str = "", expert_guidance: str = ""):
    system = prompt("critic") + "\n\nSPECIALIST SKILLS:\n" + CHILDREN_SKILLS + "\n" + PLOT_SKILLS
    user = (
        f"SPEC:\n{spec.model_dump_json()}\nOUTLINE:\n{outline.model_dump_json()}\n"
        f"STORY BIBLE:\n{bible}\nEXPERT GUIDANCE:\n{expert_guidance}\n"
        f"STORY:\n{story.model_dump_json()}"
    )
    return await llm.generate(system, user, Critique, settings.critic_model)


async def rewriter(spec: StorySpec, story: Story, critique: Critique, bible: str = "", expert_guidance: str = ""):
    system = prompt("rewriter") + "\n\nSPECIALIST SKILLS:\n" + CHILDREN_SKILLS + "\n" + PLOT_SKILLS
    user = (
        f"SPEC:\n{spec.model_dump_json()}\nSTORY BIBLE:\n{bible}\n"
        f"EXPERT GUIDANCE:\n{expert_guidance}\nSTORY:\n{story.model_dump_json()}\n"
        f"CRITIQUE:\n{critique.model_dump_json()}"
    )
    return await llm.generate(system, user, Story, settings.rewriter_model)
