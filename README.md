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

## Stack

- Python 3.11+
- FastAPI
- Pydantic
- OpenRouter
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

Copy `.env.example` to `.env` and put your OpenRouter key in it:

```env
OPENROUTER_API_KEY=...
DEFAULT_MODEL=your/model
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

## Next milestones

1. Persist StoryState and agent runs in SQLite/Postgres.
2. Move prompts into versioned files.
3. Add Story Bible and continuity tools.
4. Add specialized expert skills and evaluators.
5. Add storyboard and image generation.
6. Add background jobs/SSE for long-running generations.
