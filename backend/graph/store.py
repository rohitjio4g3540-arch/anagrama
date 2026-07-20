import json
from threading import Lock
from backend.config.settings import get_settings
from backend.models.schemas import GraphEdge, GraphNode, Source

class LocalKnowledgeGraph:
    """File-backed development adapter; replace with Neo4jGraphStore in deployment."""
    def __init__(self) -> None:
        self.path = get_settings().state_path
        self.lock = Lock()
        self.data = {"nodes": [], "edges": [], "sources": [], "projects": []}
        if self.path.exists():
            try: self.data.update(json.loads(self.path.read_text(encoding="utf-8")))
            except json.JSONDecodeError: pass

    def _save(self) -> None:
        self.path.write_text(json.dumps(self.data, indent=2, default=str), encoding="utf-8")

    def add_source(self, source: Source) -> None:
        with self.lock:
            self.data["sources"] = [s for s in self.data["sources"] if s["id"] != source.id] + [source.model_dump(mode="json")]
            self._save()

    def upsert_node(self, node: GraphNode) -> None:
        with self.lock:
            items = self.data["nodes"]
            matched = next((item for item in items if item["label"].lower() == node.label.lower() and item["type"] == node.type), None)
            if matched:
                matched["source_ids"] = sorted(set(matched.get("source_ids", []) + node.source_ids))
                matched["confidence"] = max(matched["confidence"], node.confidence)
            else: items.append(node.model_dump())
            self._save()

    def add_edge(self, edge: GraphEdge) -> None:
        with self.lock:
            if not any(item["source"] == edge.source and item["target"] == edge.target and item["relation"] == edge.relation for item in self.data["edges"]): self.data["edges"].append(edge.model_dump())
            self._save()

    def snapshot(self) -> dict: return {"nodes": self.data["nodes"], "edges": self.data["edges"], "sources": self.data["sources"]}
    def projects(self) -> list[dict]: return self.data["projects"]
    def add_project(self, project: dict) -> dict:
        with self.lock: self.data["projects"].append(project); self._save(); return project

graph = LocalKnowledgeGraph()
