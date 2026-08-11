from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .studio_persistence import add_scene, add_panel
from .models import StoryOutline

@dataclass(frozen=True)
class StoryboardResult:
    scenes: list[dict[str, Any]]
    panels: list[dict[str, Any]]

def outline_to_storyboard(project_id: str, outline: StoryOutline, panels_per_scene: int = 4) -> StoryboardResult:
    scenes=[]; panels=[]
    for scene in outline.scenes:
        saved=add_scene(project_id, scene.number, scene.title, scene.summary)
        scenes.append(saved)
        for n in range(1, panels_per_scene+1):
            panel=add_panel(scene_id=saved['id'], panel_number=n, purpose='story beat', shot='medium', camera='eye-level', action=scene.summary if n == 1 else '', visual_prompt=f"Scene {scene.number}, panel {n}: {scene.summary}")
            panels.append(panel)
    return StoryboardResult(scenes, panels)
