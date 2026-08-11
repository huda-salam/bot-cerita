from dataclasses import dataclass
from .visual_bible import VisualProfile, build_visual_prompt

@dataclass(frozen=True)
class Panel:
    number: int
    purpose: str
    shot: str
    camera: str
    setting: str
    characters: list[dict]
    action: str
    expression: str
    dialogue: str = ""
    narration: str = ""
    visual_prompt: str = ""

@dataclass(frozen=True)
class Storyboard:
    title: str
    scene_number: int
    panels: list[Panel]


def build_storyboard(title: str, scene_number: int, setting: str, characters: list[dict], beats: list[dict], visual_profiles: dict[str, VisualProfile] | None = None, style_bible: str = "") -> Storyboard:
    visual_profiles = visual_profiles or {}
    panels = []
    for i, beat in enumerate(beats, 1):
        panel_chars = beat.get("characters", characters)
        prompts = []
        for char in panel_chars:
            cid = char.get("id") if isinstance(char, dict) else None
            profile = visual_profiles.get(cid) if cid else None
            if profile:
                prompts.append(build_visual_prompt(profile, beat.get("action", ""), style_bible))
        panels.append(Panel(i, beat.get("purpose", "advance story"), beat.get("shot", "medium"), beat.get("camera", "eye level"), setting, panel_chars, beat.get("action", ""), beat.get("expression", "neutral"), beat.get("dialogue", ""), beat.get("narration", ""), "\n\n".join(prompts)))
    return Storyboard(title, scene_number, panels)
