# Bot Cerita

MVP AI Story Agent for generating short stories with a stateful orchestrator.

## Architecture

```text
Request
  -> Story Director
  -> Story Planner
  -> Writer
  -> Critic
  -> Rewriter (when needed)
  -> Final Story
```

The orchestrator owns workflow and state. LLM agents are specialized workers. Structured JSON is validated with Pydantic.

## LLM strategy

Anthropic is the default provider. The routing is intentionally asymmetric:

- **Director:** Claude Haiku 4.5 — fast and inexpensive for specification extraction.
- **Planner:** Claude Opus 4.8 — deepest reasoning for plot architecture and difficult story decisions.
- **Writer:** Claude Sonnet 5 — primary creative writing model; best balance of quality, speed, and cost.
- **Critic:** Claude Sonnet 5 — strong independent editorial evaluation without paying Opus prices on every pass.
- **Rewriter:** Claude Sonnet 5 — high-quality revision while preserving cost efficiency.

OpenRouter remains supported as an optional provider for experimentation with other models.

> Important: a Claude.ai Pro/Max subscription and Anthropic API billing are separate concepts for application runtime. Claude Pro/Max can authenticate Claude Code, while this FastAPI application needs an Anthropic API key (or OpenRouter key) to make programmatic model calls.

## Stack

- Python 3.11+
- FastAPI
- Pydantic
- Anthropic Messages API (default)
- OpenRouter (optional)
- SQLite-ready configuration

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
  "length": "medium"
}
```

## Model routing

The model names live in `.env`, so changing providers/models does not require changing agent code.

```env
DIRECTOR_MODEL=claude-haiku-4-5
PLANNER_MODEL=claude-opus-4-8
WRITER_MODEL=claude-sonnet-5
CRITIC_MODEL=claude-sonnet-5
REWRITER_MODEL=claude-sonnet-5
```

## Next milestones

1. Persist StoryState and agent runs in SQLite/Postgres.
2. Move prompts into versioned files.
3. Add Story Bible and continuity tools.
4. Add specialized expert skills and evaluators.
5. Add storyboard and image generation.
6. Add background jobs/SSE for long-running generations.
