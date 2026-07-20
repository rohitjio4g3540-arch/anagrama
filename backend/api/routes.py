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

router = APIRouter(prefix="/api")

@router.get("/health")
async def health() -> dict: return {"status": "ok", "services": "anagrama", "gemini_configured": get_settings().gemini_configured, "graph_adapter": "local"}

async def stream_events(payload: ChatRequest):
    async for event in run(payload.message, payload.project_id): yield f"data: {json.dumps(event)}\n\n"

@router.post("/stream")
async def stream(payload: ChatRequest): return StreamingResponse(stream_events(payload), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@router.post("/chat")
async def chat(payload: ChatRequest) -> dict:
    events = [event async for event in run(payload.message, payload.project_id)]
    return {"message": "".join(event.get("content", "") for event in events).strip(), "events": events, "provenance": next((event.get("citations", []) for event in events if event["type"] == "complete"), [])}

@router.post("/upload")
async def upload(file: UploadFile = File(...)) -> dict:
    permitted = {".txt", ".md", ".csv", ".json"}
    suffix = Path(file.filename or "upload.txt").suffix.lower()
    if suffix not in permitted: raise HTTPException(415, "Demo adapter currently accepts TXT, MD, CSV, and JSON. Add parser adapters for PDF/DOCX/images.")
    target = get_settings().storage_path / f"{new_id('upload')}{suffix}"
    target.write_bytes(await file.read())
    result = ingest_file(target, file.filename or target.name)
    return {"status": result["status"], "source": result["source"].model_dump(mode="json"), "concepts": result["concepts"], "chunks": result["chunks"]}

@router.get("/projects")
async def projects() -> list[dict]: return graph.projects()

@router.post("/projects")
async def create_project(payload: ProjectRequest) -> dict: return graph.add_project({"id": new_id("project"), **payload.model_dump()})

@router.get("/graph")
async def get_graph() -> dict: return graph.snapshot()

@router.get("/memory")
async def get_memory(project_id: str | None = None) -> list[dict]: return [item.model_dump(mode="json") for item in memory.all(project_id)]

@router.post("/memory")
async def add_memory(tier: str, content: str, project_id: str | None = None) -> dict: return memory.add(tier, content, project_id).model_dump(mode="json")

@router.get("/search")
async def get_search(q: str) -> list[dict]: return [item.model_dump(mode="json") for item in search(q)]
