from functools import lru_cache
from pathlib import Path
import os
from dotenv import load_dotenv
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[2]
# Local development uses .env.local; .env remains supported for deployments.
load_dotenv(PROJECT_ROOT / ".env", override=False)
load_dotenv(PROJECT_ROOT / ".env.local", override=False)

class Settings(BaseModel):
    app_name: str = "Anagrama"
    environment: str = os.getenv("ENVIRONMENT", "development")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    gemini_fallback_model: str = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.5-flash")
    nvidia_api_key: str | None = os.getenv("NVIDIA_API_KEY")
    nvidia_model: str = os.getenv("NVIDIA_MODEL")
    llm_provider: str = os.getenv("LLM_PROVIDER", "gemini")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./storage/anagrama.db")
    postgres_url: str | None = os.getenv("POSTGRES_URL")
    use_postgres: bool = os.getenv("USE_POSTGRES", "false").lower() == "true" or bool(os.getenv("POSTGRES_URL"))
    neo4j_uri: str | None = os.getenv("NEO4J_URI")
    # Vercel's filesystem is read-only except /tmp; VERCEL is set automatically in that runtime.
    # /tmp is ephemeral (not shared across instances/invocations) - fine for a demo, not for real persistence.
    storage_path: Path = Path(os.getenv("ANAGRAMA_STORAGE_PATH", "/tmp/uploads" if os.getenv("VERCEL") else "storage/uploads"))
    state_path: Path = Path(os.getenv("ANAGRAMA_STATE_PATH", "/tmp/anagrama-state.json" if os.getenv("VERCEL") else "storage/anagrama-state.json"))

    @property
    def active_database_url(self) -> str:
        """Return the active database URL based on configuration."""
        if self.use_postgres and self.postgres_url:
            url = self.postgres_url
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            return url
        return self.database_url

    @property
    def gemini_configured(self) -> bool:
        return bool(self.gemini_api_key)

@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.storage_path.mkdir(parents=True, exist_ok=True)
    settings.state_path.parent.mkdir(parents=True, exist_ok=True)
    return settings
