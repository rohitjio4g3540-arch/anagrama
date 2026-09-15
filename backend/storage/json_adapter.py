"""
JSON storage adapters for Anagrama.

These adapters maintain the existing JSON-based storage functionality, preserving
the current behavior while allowing future migration to PostgreSQL.
"""

import json
import os
from threading import Lock
from pathlib import Path
from typing import Optional, List, Dict, Any
from backend.models.schemas import Source, GraphNode, GraphEdge, Memory
from backend.storage.interface import GraphStorageInterface, MemoryStorageInterface
from backend.config.settings import get_settings
from backend.utils.ids import new_id


class JSONGraphStorage(GraphStorageInterface):
    """JSON file-backed graph storage (existing implementation)."""
    
    def __init__(self) -> None:
        settings = get_settings()
        self.path = settings.state_path
        self.lock = Lock()
        self.data = {"nodes": [], "edges": [], "sources": [], "projects": []}
        if self.path.exists():
            try:
                self.data.update(json.loads(self.path.read_text(encoding="utf-8")))
            except json.JSONDecodeError:
                pass
    
    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2, default=str), encoding="utf-8")
    
    def add_source(self, source: Source, user_id: str = None) -> None:
        with self.lock:
            self.data["sources"] = [
                s for s in self.data["sources"] if s["id"] != source.id
            ] + [source.model_dump(mode="json")]
            self._save()
    
    def upsert_node(self, node: GraphNode, user_id: str = None) -> None:
        with self.lock:
            items = self.data["nodes"]
            matched = next(
                (item for item in items 
                 if item["label"].lower() == node.label.lower() 
                 and item["type"] == node.type),
                None
            )
            if matched:
                matched["source_ids"] = sorted(set(
                    matched.get("source_ids", []) + node.source_ids
                ))
                matched["confidence"] = max(matched["confidence"], node.confidence)
            else:
                items.append(node.model_dump())
            self._save()
    
    def add_edge(self, edge: GraphEdge, user_id: str = None) -> None:
        with self.lock:
            if not any(
                item["source"] == edge.source 
                and item["target"] == edge.target 
                and item["relation"] == edge.relation
                for item in self.data["edges"]
            ):
                self.data["edges"].append(edge.model_dump())
            self._save()
    
    def snapshot(self, user_id: str = None) -> Dict[str, Any]:
        return {
            "nodes": self.data["nodes"],
            "edges": self.data["edges"],
            "sources": self.data["sources"]
        }
    
    def projects(self, user_id: str = None) -> List[Dict[str, Any]]:
        return self.data["projects"]
    
    def add_project(self, project: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            self.data["projects"].append(project)
            self._save()
            return project


class JSONMemoryStorage(MemoryStorageInterface):
    """JSON file-backed memory storage (existing implementation)."""
    
    def __init__(self) -> None:
        default = "/tmp/memory.json" if os.getenv("VERCEL") else "storage/memory.json"
        self.path = Path(os.getenv("ANAGRAMA_MEMORY_PATH", default))
        self.path.parent.mkdir(parents=True, exist_ok=True)
    
    def all(self, project_id: Optional[str] = None, user_id: Optional[str] = None) -> List[Memory]:
        items = []
        if self.path.exists():
            items = json.loads(self.path.read_text(encoding="utf-8"))
        memories = [Memory(**item) for item in items]
        return [
            item for item in memories 
            if project_id is None or item.project_id in {None, project_id}
        ]
    
    async def add(self, tier: str, content: str, project_id: Optional[str] = None, user_id: Optional[str] = None) -> Memory:
        from backend.utils.ids import new_id
        from datetime import datetime
        data = self._read()
        mem = Memory(
            id=new_id("mem"),
            tier=tier,
            content=content,
            project_id=project_id,
            created_at=datetime.utcnow()
        )
        data.append(mem.model_dump(mode="json"))
        self._write(data)
        return mem
