import re
from backend.graph.store import graph
from backend.models.schemas import SearchResult, Source
from backend.llm import get_llm
from backend.config.settings import get_settings
from backend.storage.db import SessionLocal, MemoryModel

async def search(query: str, user_id: str | None = None, limit: int = 8) -> list[SearchResult]:
    llm = get_llm()
    settings = get_settings()
    
    if llm and settings.use_postgres:
        try:
            # Semantic search using pgvector
            query_embedding = await llm.embed(query)
            
            db = SessionLocal()
            try:
                # Find most relevant memories
                results = []
                memories = db.query(MemoryModel).filter(
                    MemoryModel.deleted_at == None,
                    MemoryModel.user_id == user_id,
                    MemoryModel.embedding != None
                ).order_by(MemoryModel.embedding.cosine_distance(query_embedding)).limit(limit).all()
                
                # Currently we don't have embeddings for SourceModel in the DB, 
                # but we can do semantic search on memory and return it as a SearchResult
                # For a full implementation, we'd also embed sources.
                
                for m in memories:
                    # Construct dummy Source for memory to fit the SearchResult schema
                    source = Source(id=m.id, title=f"Memory: {m.tier}", kind="memory", content=m.content, metadata={})
                    results.append(SearchResult(source=source, score=0.9, excerpt=m.content[:280]))
                
                if results:
                    return results
            finally:
                db.close()
        except Exception as e:
            print(f"Vector search failed: {e}")

    # Fallback to keyword search
    terms = set(re.findall(r"[a-zA-Z]{3,}", query.lower()))
    snapshot = graph.snapshot(user_id=user_id) if user_id else graph.snapshot()
    results = []
    for raw in snapshot["sources"]:
        source = Source(**raw)
        haystack = f"{source.title} {source.content}".lower()
        score = sum(term in haystack for term in terms) / max(1, len(terms))
        if score: results.append(SearchResult(source=source, score=round(score, 3), excerpt=source.content[:280]))
    return sorted(results, key=lambda item: item.score, reverse=True)[:limit]

async def graph_context(query: str, user_id: str | None = None) -> list[dict]:
    terms = set(re.findall(r"[a-zA-Z]{3,}", query.lower()))
    snapshot = graph.snapshot(user_id=user_id) if user_id else graph.snapshot()
    return [node for node in snapshot["nodes"] if terms.intersection(node["label"].lower().split())][:12]
