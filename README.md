# Bot Cerita

Universe-aware AI Story Engine. Satu engine dapat digunakan untuk banyak universe, karakter, dan cerita tanpa membuat bot terpisah untuk setiap IP/world.

## Architecture

```text
                         BOT CERITA ENGINE
                                |
              +-----------------+-----------------+
              |                 |                 |
            AGENTS           UNIVERSES         SKILLS
              |                 |                 |
       Plot / Writer /     World / Canon /    Plot / Fantasy /
       Critic / Visual     Characters / Lore   Mystery / Comedy ...
              |                 |                 |
              +-----------------+-----------------+
                                |
                         ORCHESTRATOR
                                |
                              Claude
```

Current story workflow:

```text
Request
  -> Resolve Universe + Character + Canon
  -> What-If Creative Engine
  -> Story Director
  -> Story Planner
  -> Expert Panel
  -> Writer
  -> Story Bible refresh
  -> Critic
  -> Rewriter (when needed)
  -> Final Story
```

The orchestrator owns workflow and state. LLM agents are specialized workers. Structured JSON is validated with Pydantic.

## Universe model

A universe is a first-class context boundary. Characters belong to a universe; stories select a universe and zero or more characters.

```text
Universe
├── Characters
├── Canon entries
├── Lore (next milestone)
├── Locations (next milestone)
├── Timeline
└── Visual Bible (next milestone)

Story
├── selected Universe
├── selected Characters
├── Story Bible
└── Scenes
```

Canon has authority levels:

- `official` — binding
- `established` — binding
- `provisional` — usable as a hint, not a fact
- `non_canon` — never treated as canon

This lets the same engine support many original universes and, where the user has the necessary rights, licensed or owned character/world packs.

## Current API

Create a universe:

```http
POST /universes
```

```json
{"name":"Dunia Arunika","description":"A fantasy world created by the user."}
```

Add a character:

```http
POST /universes/{universe_id}/characters
```

Add canon:

```http
POST /universes/{universe_id}/canon
```

```json
{
  "category":"world_rule",
  "content":"Only trained elementalists can manipulate fire.",
  "authority":"official"
}
```

Generate a story using the universe:

```http
POST /stories
```

```json
{
  "idea":"Arka menemukan makhluk kecil di hutan",
  "universe_id":"<universe-id>",
  "character_ids":["<character-id>"],
  "target_age":"7-10",
  "genre":"fantasy",
  "tone":["warm","funny","adventurous"],
  "language":"Indonesian",
  "length":"medium",
  "what_if_count":5
}
```

## LLM strategy

Anthropic is the default provider:

- **What-If:** Claude Sonnet 5 — creative exploration and candidate scoring.
- **Director:** Claude Haiku 4.5 — fast specification extraction.
- **Planner:** Claude Opus 5 — deepest reasoning for plot architecture.
- **Expert panel:** Claude Sonnet 5 — independent specialist reviews.
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
- SQLite-ready persistence

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

## Roadmap

### 0.5 — Universe Foundation (current)
- Universe entity
- Character registry
- Canon registry with authority levels
- Universe-aware context resolver
- Story request can select universe + characters

### 0.6 — Rich World Model
- Locations
- Factions
- Lore documents
- Character relationships
- Timeline events
- Character/version history

### 0.7 — Context Engine
- Relevant-context retrieval
- Canon conflict detection
- context budgeting
- cross-story memory

### 0.8 — Visual Bible
- Character visual identity
- Universe art direction
- style profiles
- character sheets

### 0.9 — Storyboard
- scene-to-panel planning
- camera language
- dialogue/layout
- image prompts

### 1.0 — Story Studio
- image generation
- comic assembly
- long-running jobs/SSE
- evaluation/regression suite
