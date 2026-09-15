from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router
from backend.config.settings import get_settings

app = FastAPI(title="Anagrama API", version="0.1.0")
# Loosened to allow any origin for the public demo deployment (no cookies/credentials are used,
# so allow_origins=["*"] is safe here). Tighten to the deployed frontend's exact origin once known.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)

from sqlalchemy import text
from backend.storage.db import Base, engine

@app.on_event("startup")
async def startup() -> None:
    settings = get_settings()
    if settings.use_postgres and settings.active_database_url.startswith("postgresql"):
        try:
            with engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
        except Exception as e:
            print(f"Failed to create vector extension (might already exist or lack perms): {e}")
        
        try:
            Base.metadata.create_all(bind=engine)
            print("Successfully initialized Postgres tables.")
        except Exception as e:
            print(f"Failed to create tables: {e}")

