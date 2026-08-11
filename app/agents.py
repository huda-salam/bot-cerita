from .config import settings
from .llm import llm
from .models import StoryRequest, StorySpec, StoryOutline, Story, Critique

DIRECTOR = """You are the Story Director for a professional children's fiction studio. Turn the user's idea into a precise story specification. Preserve the requested audience, genre and tone. Design a clear premise, theme, setting, characters, central conflict and ending direction. Avoid generic filler. Return only valid JSON matching the requested schema."""
PLANNER = """You are a story architect. Create a scene-by-scene outline from the story specification. Every scene needs a purpose, progression and transition. Escalate conflict, protect character consistency and keep pacing appropriate for the target age. Return only valid JSON."""
WRITER = """You are an expert children's fiction writer. Write the complete story from the specification and outline. Use vivid but age-appropriate Indonesian, natural dialogue, concrete action and emotional beats. Do not introduce unexplained characters or change established facts. Return only valid JSON."""
CRITIC = """You are an independent story editor. Evaluate the story against the specification and outline. Score continuity, pacing, character quality and age appropriateness from 0-100. Identify concrete problems that a rewriter can fix. Be strict and independent. Return only valid JSON."""
REWRITER = """You are a senior fiction editor. Rewrite the story to address every meaningful issue in the critique while preserving good material, the premise, characters and target audience. Return only valid JSON."""

async def director(req: StoryRequest):
    return await llm.generate(DIRECTOR, req.model_dump_json(), StorySpec, settings.director_model)

async def planner(spec: StorySpec):
    return await llm.generate(PLANNER, spec.model_dump_json(), StoryOutline, settings.planner_model)

async def writer(spec: StorySpec, outline: StoryOutline):
    return await llm.generate(WRITER, f"SPEC:\n{spec.model_dump_json()}\nOUTLINE:\n{outline.model_dump_json()}", Story, settings.writer_model)

async def critic(spec: StorySpec, outline: StoryOutline, story: Story):
    return await llm.generate(CRITIC, f"SPEC:\n{spec.model_dump_json()}\nOUTLINE:\n{outline.model_dump_json()}\nSTORY:\n{story.model_dump_json()}", Critique, settings.critic_model)

async def rewriter(spec: StorySpec, story: Story, critique: Critique):
    return await llm.generate(REWRITER, f"SPEC:\n{spec.model_dump_json()}\nSTORY:\n{story.model_dump_json()}\nCRITIQUE:\n{critique.model_dump_json()}", Story, settings.rewriter_model)
