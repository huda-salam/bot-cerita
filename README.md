# Bot Cerita

MVP AI Story Agent for generating short stories with a stateful orchestrator and specialist skill packs.

## Architecture

```text
Request
  -> Story Director (Haiku)
  -> Story Planner (Opus)
  -> Writer (Sonnet)
  -> Critic (Sonnet)
  -> Rewriter (Sonnet, when needed)
  -> Final Story

                    +----------------+
                    |   Story Bible  |
                    +----------------+
                           ^
                           |
                    shared source of truth
```

The orchestrator owns workflow and state. LLM agents are specialized workers. Specialist skills are versionable Markdown procedures loaded into the relevant agent prompts.

## Milestone 0.2

- Anthropic direct API as the default provider.
- Current Claude model routing by agent.
- SQLite persistence for StoryState.
- Agent-run persistence foundation.
- Story Bible domain model.
- Versioned prompts in `app/prompts/`.
- Specialist skill packs in `app/skills/`.
- Plot, children's literature and dialogue guidance.
- Bounded critic/revision loop.

## Claude routing

| Agent | Model | Role |
|---|---|---|
| Director | `claude-haiku-4-5` | fast specification extraction |
| Planner | `claude-opus-5` | deep plot/structure reasoning |
| Writer | `claude-sonnet-5` | main creative generation |
| Critic | `claude-sonnet-5` | independent editorial review |
| Rewriter | `claude-sonnet-5` | targeted revision |

The model names are configurable through `.env`.

## Run locally

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# Linux/macOS
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set an Anthropic API key:

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=...
```

A Claude.ai Pro/Max subscription does not itself provide an application API key; the application needs Anthropic API access. OpenRouter can still be selected with `LLM_PROVIDER=openrouter`.

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

The response includes a story id and the generated story. SQLite state is stored in `bot_cerita.db` by default.

## Roadmap

1. Extract/update Story Bible after every scene.
2. Add independent expert evaluators for plot, age suitability and continuity.
3. Add What-If premise generator and candidate scoring.
4. Add storyboard + image prompt specialist.
5. Add background jobs/SSE for long-running generations.
6. Add RAG knowledge packs and evaluation datasets.
