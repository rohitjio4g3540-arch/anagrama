from dataclasses import dataclass, field
from backend.memory.store import memory as memory_store
from backend.models.schemas import Memory, SearchResult
from backend.retrieval.hybrid import graph_context, search

@dataclass
class AssembledContext:
    """Structured retrieval bundle for one turn: graph concepts, matching sources, and recent memory."""
    message: str
    project_id: str | None
    nodes: list[dict] = field(default_factory=list)
    sources: list[SearchResult] = field(default_factory=list)
    memories: list[Memory] = field(default_factory=list)

    @property
    def source_summary(self) -> str:
        return "; ".join(item.source.title for item in self.sources) or "your current workspace"

    @property
    def concept_summary(self) -> str:
        return ", ".join(node["label"] for node in self.nodes) or "none"

    @property
    def memory_summary(self) -> str:
        if not self.memories:
            return "no prior memory for this project"
        return "; ".join(m.content[:120] for m in self.memories)

    @property
    def citations(self) -> list[dict]:
        return [{"title": item.source.title, "source_id": item.source.id} for item in self.sources]

def build_context(message: str, project_id: str | None = None) -> AssembledContext:
    nodes = graph_context(message)
    sources = search(message)
    memories = memory_store.all(project_id)[-5:]
    return AssembledContext(message=message, project_id=project_id, nodes=nodes, sources=sources, memories=memories)
