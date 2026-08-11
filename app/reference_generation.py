from __future__ import annotations
from dataclasses import dataclass
from .image_provider import ImageGenerationRequest, ImageGenerationResult, ImageProvider
from .image_reference_adapter import ReferenceInput, build_reference_aware_request

@dataclass(frozen=True)
class ReferenceGenerationPlan:
    references: list[ReferenceInput]
    mode: str = "multi-reference"

async def generate_with_references(provider: ImageProvider, request: ImageGenerationRequest, plan: ReferenceGenerationPlan) -> ImageGenerationResult:
    enriched = build_reference_aware_request(request, plan.references)
    options = dict(enriched.options)
    options["reference_mode"] = plan.mode
    enriched = ImageGenerationRequest(prompt=enriched.prompt, context=enriched.context, width=enriched.width, height=enriched.height, model=enriched.model, options=options)
    return await provider.generate(enriched)
