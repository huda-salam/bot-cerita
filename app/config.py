from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Provider: anthropic or openrouter
    llm_provider: str = "anthropic"

    anthropic_api_key: str = ""
    anthropic_base_url: str = "https://api.anthropic.com"

    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Recommended 2026 routing: cheap director, deep planner, strong writer/editor.
    default_model: str = "claude-sonnet-5"
    director_model: str = "claude-haiku-4-5"
    planner_model: str = "claude-opus-5"
    writer_model: str = "claude-sonnet-5"
    critic_model: str = "claude-sonnet-5"
    rewriter_model: str = "claude-sonnet-5"

    critic_threshold: int = 80
    max_revisions: int = 2
    database_url: str = "sqlite:///./bot_cerita.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
