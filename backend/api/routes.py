import json
from pathlib import Path
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from backend.agents.orchestrator import run
from backend.config.settings import get_settings
from backend.graph.store import graph
from backend.ingestion.pipeline import ingest_file
from backend.memory.store import memory
from backend.models.schemas import ChatRequest, ProjectRequest
from backend.retrieval.hybrid import search
from backend.utils.ids import new_id

from backend.api.auth import router as auth_router, get_current_user
from backend.storage.db import User
from fastapi import Depends

router = APIRouter(prefix="/api")
router.include_router(auth_router, prefix="")

@router.get("/health")
async def health() -> dict: return {"status": "ok", "services": "anagrama", "gemini_configured": get_settings().gemini_configured, "graph_adapter": "local"}

@router.get("/db_test")
async def db_test() -> dict:
    from backend.storage.db import engine
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            # Check if users table exists
            table_exists = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')")).scalar()
            return {"status": "connected", "result": result, "users_table_exists": table_exists, "url": str(engine.url).split("@")[-1]}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def stream_events(payload: ChatRequest, user: User):
    async for event in run(payload.message, payload.project_id, user.id): yield f"data: {json.dumps(event)}\n\n"

@router.post("/stream")
async def stream(payload: ChatRequest, user: User = Depends(get_current_user)): 
    return StreamingResponse(stream_events(payload, user), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@router.post("/chat")
async def chat(payload: ChatRequest, user: User = Depends(get_current_user)) -> dict:
    events = [event async for event in run(payload.message, payload.project_id, user.id)]
    return {"message": "".join(event.get("content", "") for event in events).strip(), "events": events, "provenance": next((event.get("citations", []) for event in events if event["type"] == "complete"), [])}

@router.post("/upload")
async def upload(file: UploadFile = File(...), user: User = Depends(get_current_user)) -> dict:
    permitted = {".txt", ".md", ".csv", ".json"}
    suffix = Path(file.filename or "upload.txt").suffix.lower()
    if suffix not in permitted: raise HTTPException(415, "Demo adapter currently accepts TXT, MD, CSV, and JSON. Add parser adapters for PDF/DOCX/images.")
    target = get_settings().storage_path / f"{new_id('upload')}{suffix}"
    target.write_bytes(await file.read())
    result = await ingest_file(target, file.filename or target.name, user.id)
    return {"status": result["status"], "source": result["source"].model_dump(mode="json"), "concepts": result["concepts"], "chunks": result["chunks"]}

@router.get("/projects")
async def projects(user: User = Depends(get_current_user)) -> list[dict]: 
    return graph.projects(user_id=user.id)

@router.post("/projects")
async def create_project(payload: ProjectRequest, user: User = Depends(get_current_user)) -> dict: 
    return graph.add_project({"id": new_id("project"), "user_id": user.id, **payload.model_dump()})

@router.get("/graph")
async def get_graph(user: User = Depends(get_current_user)) -> dict: 
    return graph.snapshot(user_id=user.id)

@router.get("/memory")
async def get_memory(project_id: str | None = None, user: User = Depends(get_current_user)) -> list[dict]: 
    return [item.model_dump(mode="json") for item in memory.all(project_id, user.id)]

@router.post("/memory")
async def add_memory(tier: str, content: str, project_id: str | None = None, user: User = Depends(get_current_user)) -> dict: 
    memory_entry = await memory.add(tier, content, project_id, user.id)
    return memory_entry.model_dump(mode="json")

@router.get("/search")
async def get_search(q: str, user: User = Depends(get_current_user)) -> list[dict]: 
    return [item.model_dump(mode="json") for item in search(q, user.id)]
