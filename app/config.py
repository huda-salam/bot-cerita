from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    llm_provider: str = "anthropic"
    anthropic_api_key: str = ""
    anthropic_base_url: str = "https://api.anthropic.com"
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    local_llm_api_key: str = ""
    local_llm_base_url: str = "http://localhost:11434/v1"

    default_model: str = "story-writer"
    director_model: str = "story-director"
    planner_model: str = "story-planner"
    writer_model: str = "story-writer"
    critic_model: str = "story-critic"
    rewriter_model: str = "story-writer"
    expert_model: str = "story-expert"
    what_if_model: str = "story-ideas"

    model_aliases: dict[str, str] = Field(default_factory=lambda: {
        "story-director": "anthropic:claude-haiku-4-5",
        "story-planner": "anthropic:claude-opus-5",
        "story-writer": "anthropic:claude-sonnet-5",
        "story-critic": "anthropic:claude-sonnet-5",
        "story-expert": "anthropic:claude-sonnet-5",
        "story-ideas": "anthropic:claude-sonnet-5",
    })

    max_tokens: int = 8192
    llm_timeout_seconds: float = 180.0
    critic_threshold: int = 80
    max_revisions: int = 2
    database_url: str = "sqlite:///./bot_cerita.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
