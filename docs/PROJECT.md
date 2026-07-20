# PROJECT.md

> Generated from a direct read of the repository (2026-07-19). Anything not directly observable in the code is marked **Uncertain**. This file did not exist before this pass — `docs/` already contained other hand-authored docs (see [ARCHITECTURE.md](ARCHITECTURE.md) for how this pass reconciles with those).

## What this is

**Anagrama** is described in `README.md` as "an AI-native Knowledge Operating System" — a workspace for capturing information, connecting concepts, and reasoning across a personal/team knowledge base via a chat-style interface backed by a knowledge graph and tiered memory.

## What actually runs (verified in code)

- A **Next.js 16 App Router frontend** in `apps/web/` — a single-page dashboard UI (`apps/web/app/page.tsx`) with a sidebar, a chat/ask input that streams answers, an SVG "knowledge graph" widget, and several stat/summary cards. Most of the dashboard content (recent sources, agenda items, pulse numbers, the graph nodes themselves) is **hardcoded demo data**, not fetched from the backend. Only the ask/chat flow (`POST /stream`) is a real API integration.
- A **FastAPI backend** in `backend/` exposing `/health`, `/stream`, `/chat`, `/upload`, `/projects`, `/graph`, `/memory`, `/search` (confirmed against `backend/api/routes.py` and the generated OpenAPI types in `src/lib/generated/api-types.ts`).
- A single-function **orchestrator** (`backend/agents/orchestrator.py`) that: retrieves matching graph nodes and keyword-searched sources, picks a "specialist" label via simple keyword matching (no actual specialist agents or delegation logic exist), optionally calls Gemini for a real answer, and falls back to a templated sentence if no LLM is configured or the call fails.
- A **Gemini-only LLM integration** (`backend/llm/gemini.py`, via the `google-genai` SDK) with a configured fallback model if the primary model 404s.
- A **file-backed local graph/memory store** (JSON files under `storage/`) — no PostgreSQL/pgvector or Neo4j code path exists yet; those are only referenced in `docker-compose.yml` and prose docs as a future target.
- A **keyword-substring ingestion pipeline** (`backend/ingestion/pipeline.py`) — "concept extraction" is regex word-frequency ranking, not an ML/LLM extraction step.

## Important discrepancy: existing docs describe a system that was apparently rewritten out from under them

Several files already in `docs/` (`AGENT_ARCHITECTURE.md`, `ARCHITECTURE.md` prior to this pass, `README.md`) describe:
- The **OpenAI Responses API** and **OpenAI Agents SDK `handoffs`** pattern as the provider/orchestration layer
- A file `backend/agents/definitions.py` (not present on disk — the real file today is `backend/agents/orchestrator.py`)
- Distinct specialist agents (Knowledge/Research/Writing/Planning/Design/Programming) as if they were separately implemented — in the actual code these are just string labels chosen by `choose_specialist()`'s keyword matching, with **no per-specialist logic, prompts, or SDK objects**

This isn't just stale/aspirational prose: `backend/agents/__pycache__/definitions.cpython-312.pyc` exists on disk, which only happens if `definitions.py` was a real file that Python actually compiled and ran. So `backend/agents/definitions.py` most likely **did exist** (matching the OpenAI/Agents-SDK design the docs describe) and was later **replaced** by the current, simpler `orchestrator.py` — with the docs never updated for the rewrite. Whichever direction the drift went, the current code uses **Gemini** exclusively (`GEMINI_API_KEY`, `backend/llm/gemini.py`) with no OpenAI SDK dependency anywhere in `apps/api/requirements.txt`. Treat the older docs' framing of "Executive Agent" / "specialist handoff" as **describing a prior or planned implementation, not the current one**, until reconciled.

## Two frontend implementations exist — only one is live

There is a second, much simpler, unfinished frontend at the repo root: `app/page.tsx` + `src/components/chat/chat-panel.tsx` + `src/store/app-store.ts` + `src/lib/*`. The `npm run dev` script explicitly runs `next dev apps/web`, so **this root-level version is not served by any script in `package.json`**, and it appears to predate the `apps/web` build. See [current_state.md](../context/current_state.md) for why it's also currently broken if run directly.

## Tech stack

- **Frontend**: Next.js 16.2.10, React 19.2.4, Tailwind CSS v4, Framer Motion
- **Backend**: FastAPI, Pydantic v2, SQLAlchemy + psycopg (declared but unused by any code path read), `neo4j` driver (declared but unused), `google-genai`
- **Infra (declared, not yet wired to app code)**: PostgreSQL + pgvector and Neo4j via `docker-compose.yml`
