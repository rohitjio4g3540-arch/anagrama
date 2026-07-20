# Agent architecture

The Executive Agent classifies intent, retrieves source/graph/memory context, selects a specialist, synthesizes the final result, and records conversation memory. Specialist definitions live in `backend/agents/definitions.py` and use the OpenAI Agents SDK `handoffs` pattern.

Streaming events are normalized at the API boundary:

- `tool` — retrieval, memory, or graph action started
- `handoff` — Executive delegated to a specialist
- `delta` — response text increment
- `warning` — degraded dependency or provider operation
- `complete` — citations and final agent

The provider call is exclusively the OpenAI Responses API. No Assistants API surface is used.
