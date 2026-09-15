import re
import json
from pathlib import Path
from backend.graph.store import graph
from backend.models.schemas import GraphEdge, GraphNode, Source
from backend.utils.ids import new_id
from backend.llm import get_llm

async def extract_concepts(text: str) -> list[str]:
    llm = get_llm()
    if llm:
        system = "You extract exactly 10 key concepts from the user's text. Return ONLY a JSON array of strings, e.g. ['concept 1', 'concept 2']. Do not include markdown formatting or other text."
        prompt = f"Text to extract concepts from:\n{text[:5000]}"
        try:
            res = await llm.generate(system=system, prompt=prompt)
            if res:
                # Cleanup potential markdown ticks
                res = res.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
                concepts = json.loads(res)
                if isinstance(concepts, list):
                    return concepts[:10]
        except Exception as e:
            print("Failed to extract concepts via LLM, falling back to regex", e)
            
    # Fallback
    STOP = {"this", "that", "with", "from", "into", "about", "have", "will", "your", "their", "they", "than", "which", "while", "where", "when", "what", "also"}
    words = re.findall(r"[A-Za-z][A-Za-z-]{3,}", text.lower())
    ranked = sorted({word for word in words if word not in STOP}, key=lambda word: (-words.count(word), word))
    return ranked[:10]

async def ingest(title: str, content: str, kind: str = "document", metadata: dict | None = None, user_id: str | None = None) -> dict:
    """The single mandatory Capture → Parse → Chunk → Extract → Graph → Memory path."""
    source = Source(id=new_id("src"), title=title, kind=kind, content=content, metadata=metadata or {})
    graph.add_source(source, user_id=user_id)
    concepts = await extract_concepts(content)
    node_ids = []
    for concept in concepts:
        node = GraphNode(id=new_id("node"), label=concept.replace("-", " ").title(), type="concept", source_ids=[source.id])
        graph.upsert_node(node, user_id=user_id); node_ids.append(node.id)
    document = GraphNode(id=new_id("doc"), label=title, type="document", source_ids=[source.id])
    graph.upsert_node(document, user_id=user_id)
    for concept_id in node_ids[:6]: graph.add_edge(GraphEdge(id=new_id("edge"), source=document.id, target=concept_id, relation="discusses", evidence=[source.id]), user_id=user_id)
    return {"source": source, "concepts": concepts, "chunks": max(1, (len(content) + 999) // 1000), "status": "indexed"}

async def ingest_file(path: Path, filename: str, user_id: str | None = None) -> dict:
    content = path.read_text(encoding="utf-8", errors="replace")
    return await ingest(filename, content, kind="file", metadata={"path": str(path)}, user_id=user_id)
