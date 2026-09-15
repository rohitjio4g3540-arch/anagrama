# Agent architecture

> **DEPRECATED:** This document describes a previous implementation using the OpenAI Agents SDK that has been removed. The current implementation uses a single orchestrator function with Gemini integration. See [CURRENT_ARCHITECTURE.md](CURRENT_ARCHITECTURE.md) for the current implementation and [TARGET_ARCHITECTURE.md](TARGET_ARCHITECTURE.md) for the planned evolution.

---

## Historical Implementation (Removed)

The Executive Agent classifies intent, retrieves source/graph/memory context, selects a specialist, synthesizes the final result, and records conversation memory. Specialist definitions lived in `backend/agents/definitions.py` and used the OpenAI Agents SDK `handoffs` pattern.

Streaming events were normalized at the API boundary:

- `tool` — retrieval, memory, or graph action started
- `handoff` — Executive delegated to a specialist
- `delta` — response text increment
- `warning` — degraded dependency or provider operation
- `complete` — citations and final agent

The provider call was exclusively the OpenAI Responses API. No Assistants API surface was used.

---

## Current Implementation

For the current implementation, see:
- [CURRENT_ARCHITECTURE.md](CURRENT_ARCHITECTURE.md) - Current system architecture
- [ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md) - Architectural decisions
- [TARGET_ARCHITECTURE.md](TARGET_ARCHITECTURE.md) - Planned evolution
- [ROADMAP.md](ROADMAP.md) - Implementation roadmap

The current system uses:
- Single orchestrator function in `backend/agents/orchestrator.py`
- Gemini integration via `google-genai` SDK
- Keyword-based specialist selection
- Context assembly via `backend/agents/context.py`
- Specialist-specific prompts via `backend/agents/prompts/specialists.py`
