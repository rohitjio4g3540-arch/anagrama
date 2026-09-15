from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router
from backend.config.settings import get_settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Anagrama API", version="0.1.0")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": traceback.format_exc()}
    )

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

