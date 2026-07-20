from collections.abc import AsyncIterator
from backend.agents.context import build_context
from backend.llm import get_llm
from backend.memory.store import memory
from backend.prompts.specialists import build_system_prompt

SPECIALISTS = ("Knowledge", "Research", "Writing", "Planning", "Design", "Programming")

def choose_specialist(message: str) -> str:
    intent = message.lower()
    if any(word in intent for word in ("plan", "milestone", "task", "timeline")): return "Planning"
    if any(word in intent for word in ("write", "rewrite", "outline", "name")): return "Writing"
    if any(word in intent for word in ("research", "compare", "paper", "contradiction")): return "Research"
    if any(word in intent for word in ("design", "interface", "visual")): return "Design"
    if any(word in intent for word in ("code", "program", "debug")): return "Programming"
    return "Knowledge"

async def run(message: str, project_id: str | None = None) -> AsyncIterator[dict]:
    yield {"type": "tool", "name": "retrieve_graph_context"}
    yield {"type": "tool", "name": "retrieve_hierarchical_memory"}
    context = build_context(message, project_id)
    specialist = choose_specialist(message)
    yield {"type": "handoff", "from": "Executive", "to": specialist}
    answer = (
        f"I routed this through the {specialist} agent. Based on {context.source_summary}, "
        f"I see {len(context.nodes)} connected concepts and {len(context.memories)} relevant memories. "
        f"{message.strip()} is best approached as a relationship to explore, not a document to retrieve. "
        "I would begin by mapping the strongest evidence, then test the contradictions before making a recommendation."
    )
    llm = get_llm()
    if llm:
        try:
            system = build_system_prompt(specialist)
            prompt = (
                f"Question: {message}\n\n"
                f"Retrieved sources: {context.source_summary}\n"
                f"Connected concepts: {context.concept_summary}\n"
                f"Recent memory: {context.memory_summary}"
            )
            generated = await llm.generate(system=system, prompt=prompt)
            answer = generated or answer
        except Exception as error:
            yield {"type": "warning", "message": f"Gemini response unavailable; used local reasoning: {type(error).__name__}"}
    for token in answer.split(" "):
        yield {"type": "delta", "content": token + " "}
    memory.add("conversation", f"User asked: {message[:500]}", project_id)
    yield {"type": "tool", "name": "update_memory"}
    yield {"type": "complete", "specialist": specialist, "citations": context.citations}
