# MVP Production Profile — 1–3 Page Illustrated Stories

## Product focus
The first production target is an illustrated story/comic of 1–3 pages. Animation and 5–10 minute episodes remain future capabilities and must not drive MVP architecture or cost.

## Core pipeline
Idea → Story → Page Plan → Panel Plan → Character/Style References → Image Generation → Consistency Check → Page Composition → Export

## Default production assumptions
- 1 page: 4–6 panels
- 2 pages: 8–12 panels
- 3 pages: 12–18 panels
- Prefer one generated image per panel.
- Reuse approved character/background assets whenever possible.
- Use AI image generation for new visual assets and panels; avoid AI video in the MVP path.
- Keep text/dialogue separate from image generation whenever possible so dialogue can be revised without regenerating artwork.

## Cost strategy
1. Generate a low-cost draft storyboard first.
2. Generate only panels that need new artwork.
3. Reuse canonical character references and approved backgrounds.
4. Retry only failed or low-consistency panels.
5. Use premium image generation only when the configured budget allows it.
6. Record provider/model/cost metadata for every generation so the system can learn which models are economical.

## MVP quality gates
A page is production-ready when every panel has a valid specification, required characters have references, visual style follows the style bible, dialogue/captions are attached to the correct panel, failed or low-consistency generations are flagged, and final page dimensions and reading order are valid.

## Future extension
The same Story → Scene → Panel → GenerationContext lineage remains compatible with animation. Later, a panel can become a shot and receive a motion strategy selected by the cost-aware orchestrator.
