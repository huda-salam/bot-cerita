from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

@dataclass(frozen=True)
class GenerationContext:
    id: str
    panel_id: str
    character_ids: list[str] = field(default_factory=list)
    reference_assets: list[dict[str, Any]] = field(default_factory=list)
    style_bible: str = ""
    continuity_notes: list[str] = field(default_factory=list)
    negative_prompt: str = ""
    seed: int | None = None
    parent_image_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def prompt_context(self) -> str:
        refs = "\n".join(f"- {r.get('character_id','')}: {r.get('file_path','')} view={r.get('view','')} pose={r.get('pose','')} expression={r.get('expression','')} outfit={r.get('outfit','')}" for r in self.reference_assets) or "- none"
        notes = "\n".join(f"- {n}" for n in self.continuity_notes) or "- none"
        return ("CHARACTER/STYLE CONSISTENCY\n"
                f"Characters: {', '.join(self.character_ids) or 'none'}\n"
                f"References:\n{refs}\nStyle Bible:\n{self.style_bible or '- none'}\n"
                f"Continuity:\n{notes}\nNegative Prompt:\n{self.negative_prompt or '- none'}")

def build_generation_context(panel_id: str, character_ids: list[str], reference_assets: list[dict[str, Any]], style_bible: str = "", continuity_notes: list[str] | None = None, negative_prompt: str = "", seed: int | None = None, parent_image_id: str | None = None, metadata: dict[str, Any] | None = None) -> GenerationContext:
    return GenerationContext(id=str(uuid4()), panel_id=panel_id, character_ids=character_ids, reference_assets=reference_assets, style_bible=style_bible, continuity_notes=continuity_notes or [], negative_prompt=negative_prompt, seed=seed, parent_image_id=parent_image_id, metadata=metadata or {})
