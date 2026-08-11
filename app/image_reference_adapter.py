from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from .image_provider import ImageGenerationRequest

@dataclass(frozen=True)
class ReferenceInput:
    asset_id: str
    file_path: str = ""
    role: str = "character"
    strength: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

def build_reference_aware_request(request: ImageGenerationRequest, references: list[ReferenceInput]) -> ImageGenerationRequest:
    options = dict(request.options)
    options["references"] = [{"asset_id": r.asset_id, "file_path": r.file_path, "role": r.role, "strength": r.strength, "metadata": r.metadata} for r in references]
    options["reference_mode"] = "multi-reference"
    return ImageGenerationRequest(prompt=request.prompt, context=request.context, width=request.width, height=request.height, model=request.model, options=options)
