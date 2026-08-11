from dataclasses import dataclass, asdict
from .asset_registry import list_character_assets

@dataclass(frozen=True)
class VisualProfile:
    character_id: str
    references: list[dict]
    anchors: list[str]
    appearance: str = ""


def build_character_visual_profile(character_id: str, appearance: str = "") -> VisualProfile:
    assets = list_character_assets(character_id)
    refs = []
    anchors = []
    for asset in assets:
        if not asset.is_canon:
            continue
        refs.append(asdict(asset))
        for value in (asset.view, asset.pose, asset.expression, asset.outfit, asset.age):
            if value and value not in anchors:
                anchors.append(value)
    return VisualProfile(character_id, refs, anchors, appearance)


def build_visual_prompt(profile: VisualProfile, scene_description: str, style_bible: str = "") -> str:
    refs = "\n".join("- {file_path} ({view}, {pose}, {expression}, {outfit}, age={age})".format(**r) for r in profile.references)
    anchors = ", ".join(profile.anchors)
    return """CHARACTER VISUAL CANON\nCharacter ID: {character_id}\nAppearance: {appearance}\nVisual anchors: {anchors}\nReference assets:\n{refs}\n\nSTYLE BIBLE:\n{style}\n\nSCENE:\n{scene}\n\nInstruction: preserve the registered visual canon. Do not invent or alter core identity, face, body proportions, signature clothing, colors, or other established visual anchors unless the scene explicitly requires a canon-approved change.""".format(character_id=profile.character_id, appearance=profile.appearance, anchors=anchors, refs=refs or "- none registered", style=style_bible, scene=scene_description)
