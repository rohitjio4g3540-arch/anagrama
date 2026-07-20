from backend.prompts.executive import EXECUTIVE_INSTRUCTIONS

SPECIALIST_FOCUS = {
    "Knowledge": "Prioritize connecting ideas across sources. Surface the strongest relationships and name what's still uncertain.",
    "Research": "Compare evidence across sources, name contradictions explicitly, and avoid overstating confidence where evidence is thin.",
    "Writing": "Prioritize clarity and structure. Propose a concrete outline or phrasing, not just a description of what to write.",
    "Planning": "Turn the request into concrete next steps with an order of operations. Call out dependencies and blockers.",
    "Design": "Reason about the interface or visual implications. Ground suggestions in what's already been captured, not generic design advice.",
    "Programming": "Be concrete about code-level tradeoffs. Only reference retrieved context if it's actually relevant to the technical question.",
}

def build_system_prompt(specialist: str) -> str:
    """One tailored system prompt per specialist, built on the shared Executive persona."""
    focus = SPECIALIST_FOCUS.get(specialist, SPECIALIST_FOCUS["Knowledge"])
    return f"{EXECUTIVE_INSTRUCTIONS}\n\nYou are currently acting as the {specialist} specialist. {focus}"
