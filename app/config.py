from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # MVP default: OpenRouter free model.
    llm_provider: str = "openrouter"
    anthropic_api_key: str = ""
    anthropic_base_url: str = "https://api.anthropic.com"
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    # auto = use OpenRouter model capabilities; enabled = force JSON Schema; disabled = prompt+parser fallback.
    openrouter_structured_outputs: str = "auto"
    local_llm_api_key: str = ""
    local_llm_base_url: str = "http://localhost:11434/v1"

    # Provider-neutral logical models.
    default_model: str = "story-writer"
    director_model: str = "story-director"
    planner_model: str = "story-planner"
    writer_model: str = "story-writer"
    critic_model: str = "story-critic"
    rewriter_model: str = "story-writer"
    expert_model: str = "story-expert"
    what_if_model: str = "story-ideas"

    # MVP: one fixed free model for a clean baseline across every agent.
    model_aliases: dict[str, str] = Field(default_factory=lambda: {
        "story-director": "openrouter:nvidia/nemotron-3-ultra-550b-a55b:free",
        "story-planner": "openrouter:nvidia/nemotron-3-ultra-550b-a55b:free",
        "story-writer": "openrouter:nvidia/nemotron-3-ultra-550b-a55b:free",
        "story-critic": "openrouter:nvidia/nemotron-3-ultra-550b-a55b:free",
        "story-expert": "openrouter:nvidia/nemotron-3-ultra-550b-a55b:free",
        "story-ideas": "openrouter:nvidia/nemotron-3-ultra-550b-a55b:free",
    })

    # Previous Anthropic baseline is intentionally retained for later benchmark/
    # premium mode. It is NOT deleted; switch aliases when needed.
    # "story-director": "anthropic:claude-haiku-4-5",
    # "story-planner": "anthropic:claude-opus-5",
    # "story-writer": "anthropic:claude-sonnet-5",
    # "story-critic": "anthropic:claude-sonnet-5",
    # "story-expert": "anthropic:claude-sonnet-5",
    # "story-ideas": "anthropic:claude-sonnet-5",

    # LLM debugging. Disabled by default; enable locally when diagnosing provider/model issues.
    llm_debug: bool = False
    llm_log_dir: str = "logs/llm"

    max_tokens: int = 8192
    llm_timeout_seconds: float = 180.0
    critic_threshold: int = 80
    max_revisions: int = 2
    database_url: str = "sqlite:///./bot_cerita.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
