import re
from backend.graph.store import graph
from backend.models.schemas import SearchResult, Source

def search(query: str, limit: int = 8) -> list[SearchResult]:
    terms = set(re.findall(r"[a-zA-Z]{3,}", query.lower()))
    results = []
    for raw in graph.snapshot()["sources"]:
        source = Source(**raw)
        haystack = f"{source.title} {source.content}".lower()
        score = sum(term in haystack for term in terms) / max(1, len(terms))
        if score: results.append(SearchResult(source=source, score=round(score, 3), excerpt=source.content[:280]))
    return sorted(results, key=lambda item: item.score, reverse=True)[:limit]

def graph_context(query: str) -> list[dict]:
    terms = set(re.findall(r"[a-zA-Z]{3,}", query.lower()))
    return [node for node in graph.snapshot()["nodes"] if terms.intersection(node["label"].lower().split())][:12]
