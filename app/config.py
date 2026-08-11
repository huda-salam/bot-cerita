from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    default_model: str = "openai/gpt-4o-mini"
    director_model: str = ""
    planner_model: str = ""
    writer_model: str = ""
    critic_model: str = ""
    rewriter_model: str = ""
    critic_threshold: int = 80
    max_revisions: int = 2
    database_url: str = "sqlite:///./bot_cerita.db"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
