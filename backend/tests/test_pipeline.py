from backend.graph.store import graph
from backend.ingestion.pipeline import extract_concepts, ingest
from backend.retrieval.hybrid import search

def test_concept_extraction_is_deterministic():
    assert "attention" in extract_concepts("Attention shapes attention through interface design.")

def test_ingestion_updates_graph_and_retrieval():
    result = ingest("Attention study", "Attention changes when interfaces make friction visible.")
    snapshot = graph.snapshot()
    assert result["status"] == "indexed"
    assert any(source["id"] == result["source"].id for source in snapshot["sources"])
    assert search("attention")
