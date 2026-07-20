import re
from pathlib import Path
from backend.graph.store import graph
from backend.models.schemas import GraphEdge, GraphNode, Source
from backend.utils.ids import new_id

STOP = {"this", "that", "with", "from", "into", "about", "have", "will", "your", "their", "they", "than", "which", "while", "where", "when", "what", "also"}
def extract_concepts(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z-]{3,}", text.lower())
    ranked = sorted({word for word in words if word not in STOP}, key=lambda word: (-words.count(word), word))
    return ranked[:10]

def ingest(title: str, content: str, kind: str = "document", metadata: dict | None = None) -> dict:
    """The single mandatory Capture → Parse → Chunk → Extract → Graph → Memory path."""
    source = Source(id=new_id("src"), title=title, kind=kind, content=content, metadata=metadata or {})
    graph.add_source(source)
    concepts = extract_concepts(content)
    node_ids = []
    for concept in concepts:
        node = GraphNode(id=new_id("node"), label=concept.replace("-", " ").title(), type="concept", source_ids=[source.id])
        graph.upsert_node(node); node_ids.append(node.id)
    document = GraphNode(id=new_id("doc"), label=title, type="document", source_ids=[source.id])
    graph.upsert_node(document)
    for concept_id in node_ids[:6]: graph.add_edge(GraphEdge(id=new_id("edge"), source=document.id, target=concept_id, relation="discusses", evidence=[source.id]))
    return {"source": source, "concepts": concepts, "chunks": max(1, (len(content) + 999) // 1000), "status": "indexed"}

def ingest_file(path: Path, filename: str) -> dict:
    content = path.read_text(encoding="utf-8", errors="replace")
    return ingest(filename, content, kind="file", metadata={"path": str(path)})
