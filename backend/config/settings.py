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
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./storage/anagrama.db")
    neo4j_uri: str | None = os.getenv("NEO4J_URI")
    # Vercel's filesystem is read-only except /tmp; VERCEL is set automatically in that runtime.
    # /tmp is ephemeral (not shared across instances/invocations) - fine for a demo, not for real persistence.
    storage_path: Path = Path(os.getenv("ANAGRAMA_STORAGE_PATH", "/tmp/uploads" if os.getenv("VERCEL") else "storage/uploads"))
    state_path: Path = Path(os.getenv("ANAGRAMA_STATE_PATH", "/tmp/anagrama-state.json" if os.getenv("VERCEL") else "storage/anagrama-state.json"))

    @property
    def gemini_configured(self) -> bool:
        return bool(self.gemini_api_key)

@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.storage_path.mkdir(parents=True, exist_ok=True)
    settings.state_path.parent.mkdir(parents=True, exist_ok=True)
    return settings
