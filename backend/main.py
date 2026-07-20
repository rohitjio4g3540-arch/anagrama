from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router
from backend.config.settings import get_settings

app = FastAPI(title="Anagrama API", version="0.1.0")
# Loosened to allow any origin for the public demo deployment (no cookies/credentials are used,
# so allow_origins=["*"] is safe here). Tighten to the deployed frontend's exact origin once known.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)

@app.on_event("startup")
async def startup() -> None: get_settings()
