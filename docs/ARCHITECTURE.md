# ARCHITECTURE.md

> Rewritten from a direct read of the code (2026-07-19), replacing a prior 17-line version of this file. The prior version (and `AGENT_ARCHITECTURE.md`, `DEPLOYMENT.md`, `README.md`) describe an OpenAI Agents-SDK-based design that **does not match the current implementation** — see the "Discrepancy" section below. Sections marked **Uncertain** could not be fully confirmed from this repo alone.

## Data flow (as implemented)

```
apps/web/app/page.tsx  (client component)
      │  POST /stream  { message, project_id }
      ▼
backend/main.py  (FastAPI app, CORS locked to http://localhost:3000)
      │
      ▼
backend/api/routes.py  → backend/agents/orchestrator.py :: run()
      │
      ├─ backend/retrieval/hybrid.py :: graph_context(), search()   (keyword match over local graph/sources)
      ├─ backend/memory/store.py :: memory.all()                   (last 5 memory items for the project)
      ├─ choose_specialist(message)                                 (keyword match → one of 6 labels, no actual delegation)
      ├─ backend/llm/gemini.py :: GeminiProvider.generate()          (if GEMINI_API_KEY set; else templated fallback string)
      └─ memory.add("conversation", ...)                             (records the user's message, not the answer)
      │
      ▼
SSE stream of {type: tool|handoff|delta|warning|complete} events  (JSON lines prefixed "data: ")
```

- `/chat` (non-streaming) runs the same `run()` generator to completion and returns the concatenated text plus the `complete` event's citations.
- `/upload` accepts only `.txt`, `.md`, `.csv`, `.json` (explicit `415` for anything else), writes the file under `storage/uploads/`, then calls `ingest_file()`.
- `/graph`, `/memory`, `/projects`, `/search` are thin reads/writes over the same local JSON-backed stores.

## Storage (current, local-only)

- **`backend/graph/store.py`**: `LocalKnowledgeGraph` — a single JSON file at `settings.state_path` (`storage/anagrama-state.json`), holding `nodes`, `edges`, `sources`, `projects` in memory with a thread lock, rewritten in full on every write.
- **`backend/memory/store.py`**: `HierarchicalMemory` — a single JSON file at `storage/memory.json`, same read-all/rewrite-all pattern.
- Both are explicitly documented in code comments as **development adapters** intended to be replaced (by Neo4j and Postgres/pgvector respectively) — but no such adapter code exists in this repo yet. `docker-compose.yml` provisions `pgvector/pgvector:pg16` and `neo4j:5-community` containers, and `.env.example` / `backend/config/settings.py` define `DATABASE_URL`, `POSTGRES_URL`, `VECTOR_DB_URL`, `NEO4J_URI`/`NEO4J_USERNAME`/`NEO4J_PASSWORD` — but none of these are read by any store/connection code. **Uncertain**: whether this migration is in progress elsewhere or just scaffolded.

## Ingestion (`backend/ingestion/pipeline.py`)

The "Capture → Parse → Chunk → Extract → Graph → Memory" pipeline described in `docs/KNOWLEDGE_GRAPH.md` is real but simple:
- "Extraction" is `extract_concepts()`: a regex word-frequency ranker over lowercase text (words ≥4 letters, minus a small stopword list), taking the top 10 by frequency.
- "Chunking" is just `ceil(len(content) / 1000)` — a count, not an actual chunk list.
- Each concept becomes a `GraphNode` (type `concept`), the document itself becomes a `GraphNode` (type `document`), and up to 6 concept nodes get a `discusses` edge from the document node.
- There is no PDF/DOCX/image/web/GitHub/YouTube ingestion — `docs/VALIDATION_CHECKLIST.md` already flags this as an open item, and it's consistent with what's in the code (`/upload` explicitly rejects anything but plain text/markdown/CSV/JSON).

## Orchestrator / "agents" (`backend/agents/orchestrator.py`)

Still **one** function, `run()`, not a multi-agent SDK — but as of 2026-07-19 it has a real context-assembly and per-specialist prompt-engineering layer (`backend/agents/context.py`, `backend/prompts/specialists.py`), replacing the earlier version where the specialist label was purely cosmetic:
1. Emits a `tool` event for graph-context retrieval.
2. Emits a `tool` event for memory retrieval.
3. `backend/agents/context.py :: build_context()` gathers graph nodes, matching sources, and the last 5 memory entries for the project into one `AssembledContext` object (this replaces what used to be ad hoc string-building inline in `run()`).
4. Calls `choose_specialist(message)` — still a plain `if/elif` keyword matcher over 6 fixed labels (Planning, Writing, Research, Design, Programming, else Knowledge) — and emits a `handoff` event with that label.
5. Builds a templated fallback sentence, then — only if `GEMINI_API_KEY` is configured — calls `GeminiProvider.generate()` with **a system prompt selected per specialist** (`backend/prompts/specialists.py :: build_system_prompt()`, built on the shared `EXECUTIVE_INSTRUCTIONS` base plus a specialist-specific focus paragraph) and a prompt built from the assembled context (sources, concepts, and memory, not just sources). This is real, verified: a live `/stream` call routed to "Planning" returned an answer that opened with "As the Planning Specialist for Anagrama, I have mapped out a concrete, relation-based plan..." — the specialist identity is now actually shaping Gemini's output, not just labeling it.
6. Streams the answer back **word-by-word** as `delta` events (still not true token streaming from the model — the whole answer is generated first, then split on spaces).
7. Records the user's message (not the answer) to memory, and emits a final `complete` event with specialist label + citations (now sourced from `context.citations`).

This is a genuine context-engineering + prompt-engineering layer, built on the existing Gemini-only stack rather than the OpenAI Agents SDK the older docs describe (see below) — each specialist gets a distinct, tested system prompt, but there is still only one LLM call per turn (not one call per specialist/agent), so this is not a multi-agent handoff system in the OpenAI Agents SDK sense.

### Discrepancy with other `docs/` files — this looks like an undocumented rewrite, not aspirational drift

`docs/AGENT_ARCHITECTURE.md` and the pre-existing `docs/ARCHITECTURE.md` describe "the Executive Agent classifies intent... Specialist definitions live in `backend/agents/definitions.py`... using the OpenAI Agents SDK `handoffs` pattern... provider call is exclusively the OpenAI Responses API." That file does not exist on disk today — but **`backend/agents/__pycache__/definitions.cpython-312.pyc` does**, sitting right next to `orchestrator.cpython-312.pyc`. A `.pyc` file is only ever produced by Python actually compiling a same-named `.py` source file, so `backend/agents/definitions.py` demonstrably existed and ran on this machine at some point.

The most likely story: an earlier, OpenAI-Agents-SDK-based `definitions.py` orchestrator was built (matching what the docs describe), then rewritten into the current, much simpler `orchestrator.py` (Gemini-only, keyword-matched specialist labels, no SDK) — and the prose docs (`AGENT_ARCHITECTURE.md`, the old `ARCHITECTURE.md`, `DEPLOYMENT.md`, `README.md`) were never updated to match. This is a **regression/rewrite that the docs missed**, not a case of documentation written ahead of unbuilt code. Either way, there is no OpenAI SDK dependency in `apps/api/requirements.txt` today, no `OPENAI_API_KEY` read anywhere in `backend/`, and the only working LLM path is Gemini — so the docs are wrong about the *current* system regardless of which direction the drift went. Flagged here rather than silently corrected in those other files, since this pass was scoped to `PROJECT.md`/`ARCHITECTURE.md`/`repository_map.md`/`current_state.md` only. (Note: `__pycache__/` is gitignored, so this evidence exists only on this machine's disk, not in any commit — it could be cleared by a fresh checkout or a `find -delete`, so capture it now if it's useful.)

## Frontend (`apps/web/`)

- `app/layout.tsx` loads three Google fonts (Geist, Geist Mono, Fraunces-as-wordmark) and sets metadata/favicon to `/logo.png`.
- `app/page.tsx` is a single large client component: a fixed sidebar (nav labels are inert — clicking just sets local `active` state, no routing), a header, a two-column dashboard grid (an "in focus" inquiry card, a "knowledge pulse" stat card, an "unresolved tension" card, a recent-activity list, a knowledge-graph panel, a next-actions list, and an AI "pattern" callout card), and a sticky ask/chat input at the bottom.
  - **Only the ask input is wired to the backend** (`POST /stream`, streamed and parsed as SSE `delta`/`tool` events); everything else on the page (sources, agenda, pulse numbers, "Mira Chen" greeting, the graph's nodes/edges) is **inline hardcoded demo data** in the component, not fetched from `/graph`, `/memory`, `/projects`, or `/search`.
  - If the `/stream` fetch throws, it falls back to locally-typewritten canned text — meaning the dashboard "looks alive" even with the API fully offline.
- `components/knowledge-graph.tsx` renders a fixed, hand-authored 7-node/10-edge SVG graph with hover/focus interactions (via Framer Motion) — it is a **visual mock**, not a rendering of `/graph`'s actual response.
- `components/ui/button.tsx` and `card.tsx` are minimal style wrappers, no logic.

## Frontend build wiring

- No `apps/web/package.json` exists — the single root `package.json`'s scripts (`next dev apps/web`, `next build apps/web`, `next start apps/web`, `eslint apps/web`) target the subdirectory directly, and `apps/web/tsconfig.json` just extends the root `tsconfig.json`. This is not a formal npm/pnpm workspace (no `workspaces` field in `package.json`) — it works because Next.js accepts a directory argument.
- `apps/api/` contains only `requirements.txt` — there is no Python package or app code inside `apps/api/`; the actual FastAPI app lives in the top-level `backend/` package, run via `uvicorn backend.main:app`.

## Root-level `app/` + `src/` — a separate, unused frontend

A second, much plainer implementation exists at the repo root: `app/page.tsx` (renders `<ChatPanel />`), `src/components/chat/chat-panel.tsx`, `src/store/app-store.ts` (Zustand store), `src/lib/{api,stream,types}.ts`, plus `src/lib/src/lib/{projects,upload}.ts` (a duplicated `src/lib/src/lib/` nesting — almost certainly an accidental path mistake when these files were generated/moved).

- Not reachable through any `package.json` script — `next dev`/`next build`/`next start` are all pinned to `apps/web`.
- Would fail even if run directly: `src/store/app-store.ts` imports `zustand`, which is **not listed** in `package.json` dependencies or devDependencies.
- Reads as an earlier draft superseded by `apps/web`, left in place rather than removed.

## Environment variables (collected from `process.env`/`os.getenv` usage across the repo)

| Variable | Read by | Notes |
|---|---|---|
| `GEMINI_API_KEY` | `backend/config/settings.py` | Enables the real Gemini call; without it, orchestrator always uses the templated fallback |
| `GEMINI_MODEL` | `backend/config/settings.py` | Defaults to `gemini-2.5-flash` |
| `GEMINI_FALLBACK_MODEL` | `backend/config/settings.py` | Defaults to `gemini-3.5-flash`; used only if the primary model 404s |
| `DATABASE_URL` | `backend/config/settings.py` | Defaults to a local SQLite path; **not actually connected to anywhere** in the code read |
| `POSTGRES_URL`, `VECTOR_DB_URL` | `.env.example` only | Not read by any Python file found in `backend/` |
| `NEO4J_URI` | `backend/config/settings.py` | Stored on `Settings` but never used to open a driver connection |
| `NEO4J_USERNAME`, `NEO4J_PASSWORD` | `.env.example` / `docker-compose.yml` only | Not read anywhere in `backend/` |
| `ANAGRAMA_STORAGE_PATH` | `backend/config/settings.py` | Where uploaded files are written |
| `NEXT_PUBLIC_API_URL` | `apps/web/app/page.tsx`, `src/lib/api.ts` | Client-exposed API base URL, defaults to `http://localhost:8000` (two slightly different fallback strings across the two frontends — **not a functional issue** since only one frontend is live) |
| `ENVIRONMENT` | `backend/config/settings.py` | Defaults to `"development"`; not observed to change any behavior in code read |

## Notable gap: `.env.local` is not gitignored

`.gitignore` only lists `.env`, not `.env.local`. An untracked `.env.local` (68 bytes) exists at the repo root but Next.js/`load_dotenv` both treat `.env.local` as a real local-secrets file. If someone runs a broad `git add`, this file would be staged. Contents were not read as part of this pass (avoided intentionally). Recommend adding `.env.local` (and `.env*.local`) to `.gitignore`.
