import json
import os
from pathlib import Path
from backend.models.schemas import Memory
from backend.utils.ids import new_id

class HierarchicalMemory:
    def __init__(self) -> None:
        default = "/tmp/memory.json" if os.getenv("VERCEL") else "storage/memory.json"
        self.path = Path(os.getenv("ANAGRAMA_MEMORY_PATH", default))
        self.path.parent.mkdir(parents=True, exist_ok=True)
    def all(self, project_id: str | None = None) -> list[Memory]:
        items = json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else []
        memories = [Memory(**item) for item in items]
        return [item for item in memories if project_id is None or item.project_id in {None, project_id}]
    def add(self, tier: str, content: str, project_id: str | None = None) -> Memory:
        memory = Memory(id=new_id("mem"), tier=tier, content=content, project_id=project_id)
        items = [item.model_dump(mode="json") for item in self.all()] + [memory.model_dump(mode="json")]
        self.path.write_text(json.dumps(items, indent=2), encoding="utf-8")
        return memory
memory = HierarchicalMemory()
