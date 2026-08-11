# Bot Cerita

MVP AI Story Agent for generating short stories with a stateful orchestrator and specialist expert layer.

## Architecture

```text
Request
  -> What-If Creative Engine
  -> Story Director
  -> Story Planner
  -> Expert Panel
       |- Plot Expert
       |- Children's Literature Expert
       `- Character Expert
  -> Writer
  -> Critic
  -> Rewriter (when needed)
  -> Final Story
```

The orchestrator owns workflow and state. LLM agents are specialized workers. Structured JSON is validated with Pydantic.

## Why the expert layer exists

The system deliberately separates **knowledge/skill** from the writer. Before prose is generated, independent specialists review the story architecture and provide actionable guidance. This makes the writer better without turning the writer prompt into an unmaintainable mega-prompt.

The What-If engine explores materially different premises before the Director commits to one direction. Candidates are scored for novelty, emotional potential, age fit, and overall story potential.

## LLM strategy

Anthropic is the default provider:

- **What-If:** Claude Sonnet 5 — creative exploration and candidate scoring.
- **Director:** Claude Haiku 4.5 — fast specification extraction.
- **Planner:** Claude Opus 5 — deepest reasoning for plot architecture.
- **Expert panel:** Claude Sonnet 5 — three independent specialist reviews in parallel.
- **Writer:** Claude Sonnet 5 — primary creative writing model.
- **Critic:** Claude Sonnet 5 — independent editorial evaluation.
- **Rewriter:** Claude Sonnet 5 — high-quality revision.

OpenRouter remains available as an optional provider for experimentation with other models.

## Stack

- Python 3.11+
- FastAPI
- Pydantic
- Anthropic Messages API (default)
- OpenRouter (optional)
- SQLite-ready state persistence

## Run locally

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# Linux/macOS
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and configure Anthropic:

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=...
```

Start:

```bash
uvicorn app.main:app --reload
```

Health check: `GET /health`

Generate a story with `POST /stories`:

```json
{
  "idea": "Seorang anak menemukan naga kecil di gudang",
  "target_age": "7-10",
  "genre": "fantasy",
  "tone": ["funny", "warm", "adventurous"],
  "language": "Indonesian",
  "length": "medium",
  "what_if_count": 5
}
```

## Model routing

Model names live in `.env`, so changing the routing does not require changing agent code.

```env
WHAT_IF_MODEL=claude-sonnet-5
DIRECTOR_MODEL=claude-haiku-4-5
PLANNER_MODEL=claude-opus-5
EXPERT_MODEL=claude-sonnet-5
WRITER_MODEL=claude-sonnet-5
CRITIC_MODEL=claude-sonnet-5
REWRITER_MODEL=claude-sonnet-5
```

## Next milestones

1. Persist expert runs and token/cost telemetry.
2. Add Story Bible mutation/continuity tools after each scene.
3. Add genre/domain skill registry and dynamic skill selection.
4. Add storyboard + character consistency + image generation.
5. Add background jobs/SSE for long-running generations.
6. Add automated evaluation datasets and regression tests.
