from backend.agents.context import build_context
from backend.agents.orchestrator import choose_specialist
from backend.prompts.specialists import build_system_prompt

def test_build_context_returns_structured_bundle():
    context = build_context("What connects attention and friction?", project_id=None)
    assert context.message == "What connects attention and friction?"
    assert isinstance(context.source_summary, str)
    assert isinstance(context.concept_summary, str)
    assert isinstance(context.memory_summary, str)
    assert isinstance(context.citations, list)

def test_each_specialist_gets_a_distinct_system_prompt():
    prompts = {specialist: build_system_prompt(specialist) for specialist in
               ("Knowledge", "Research", "Writing", "Planning", "Design", "Programming")}
    assert len(set(prompts.values())) == len(prompts)
    for specialist, prompt in prompts.items():
        assert specialist in prompt

def test_unknown_specialist_falls_back_to_knowledge_prompt():
    assert build_system_prompt("Unknown") == build_system_prompt("Unknown")
    assert "specialist" in build_system_prompt("Unknown")

def test_choose_specialist_still_routes_by_keyword():
    assert choose_specialist("Help me plan a timeline") == "Planning"
    assert choose_specialist("Debug this code") == "Programming"
