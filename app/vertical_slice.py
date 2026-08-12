from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .models import StoryRequest
from .orchestrator import run_story
from .storyboard_workflow import outline_to_storyboard
from .character_assets import asset_registry
from .panel_references import resolve_panel_references
from .image_consistency import build_consistency_spec, augment_prompt
from .image_generation import ImageRequest, image_router

@dataclass(frozen=True)
class VerticalSliceResult:
    story: dict[str, Any]
    storyboard: dict[str, Any]
    reference_map: list[dict[str, Any]]
    image_requests: list[dict[str, Any]]
    generated_images: list[dict[str, Any]]

async def run_vertical_slice(request: StoryRequest, project_id: str, panels_per_scene: int = 3, generate_images: bool = False) -> VerticalSliceResult:
    state = await run_story(request)
    if not state.outline or not state.story:
        raise ValueError("Story workflow did not produce story and outline")
    board = outline_to_storyboard(project_id, state.outline, panels_per_scene)
    references=[]; image_requests=[]; generated_images=[]
    for panel in board.panels:
        for character_id in request.character_ids:
            assets=[a.__dict__ for a in asset_registry.list(character_id)]
            resolved=resolve_panel_references(panel["id"], character_id, assets, {}, 3)
            spec=build_consistency_spec([character_id], resolved.selected_assets)
            prompt=augment_prompt(panel.get("visual_prompt", ""), spec)
            req=ImageRequest(prompt=prompt, negative_prompt=spec.negative_prompt, reference_assets=resolved.selected_assets, metadata={"panel_id":panel["id"],"character_id":character_id})
            image_requests.append({"panel_id":panel["id"],"character_id":character_id,"request":req.__dict__})
            references.append({"panel_id":panel["id"],"character_id":character_id,"selected":resolved.selected_assets,"candidates":resolved.candidates})
            if generate_images:
                generated=await image_router.generate(req,"image-draft")
                generated_images.extend([g.__dict__ | {"panel_id":panel["id"],"character_id":character_id} for g in generated])
    return VerticalSliceResult(
        story={"id":state.id,"title":state.story.title,"story":"\n\n".join(state.story.scenes),"score":state.critique.overall_score if state.critique else 0,"revisions":state.revisions},
        storyboard={"scenes":board.scenes,"panels":board.panels}, reference_map=references, image_requests=image_requests, generated_images=generated_images)
