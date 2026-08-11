from __future__ import annotations
from .image_provider import ImageGenerationRequest, registry
from .image_reference_adapter import ReferenceInput
from .reference_generation import ReferenceGenerationPlan, generate_with_references
from .visual_context import build_generation_context

async def run_benchmark_case(case, provider_name: str, model: str | None = None):
    provider = registry.get(provider_name)
    references = [ReferenceInput(asset_id=asset_id) for asset_id in case.reference_asset_ids]
    context = build_generation_context(panel_id=f"benchmark:{case.id}", character_ids=[], reference_assets=[{"asset_id": r.asset_id, "role": r.role, "strength": r.strength} for r in references], metadata={"benchmark_case_id": case.id})
    results: list[dict] = []
    for index, prompt in enumerate(case.panel_prompts, start=1):
        request = ImageGenerationRequest(prompt=prompt, context=context, model=model, options={"benchmark_case_id": case.id, "panel_index": index})
        if references:
            result = await generate_with_references(provider, request, ReferenceGenerationPlan(references=references))
        else:
            result = await provider.generate(request)
        results.append({"panel_index": index, "prompt": prompt, "status": result.status, "url": result.url, "file_path": result.file_path, "seed": result.seed, "metadata": result.metadata})
    return results
