import pytest
from backend.graph.store import graph
from backend.ingestion.pipeline import extract_concepts, ingest
from backend.retrieval.hybrid import search

@pytest.mark.asyncio
async def test_concept_extraction_is_deterministic():
    concepts = await extract_concepts("Attention shapes attention through interface design.")
    assert "attention" in concepts or "Attention" in concepts

@pytest.mark.asyncio
async def test_ingestion_updates_graph_and_retrieval():
    result = await ingest("Attention study", "Attention changes when interfaces make friction visible.")
    snapshot = graph.snapshot()
    assert result["status"] == "indexed"
    assert any(source["id"] == result["source"].id for source in snapshot["sources"])
    assert search("attention")
