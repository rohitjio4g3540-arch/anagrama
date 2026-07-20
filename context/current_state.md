# current_state.md

> Snapshot as of 2026-07-19. What exists vs. what's aspirational/referenced-but-missing, and open uncertainties.

## What's actually built and working (verified by reading the code)

- A FastAPI backend with 8 real routes (`/health`, `/stream`, `/chat`, `/upload`, `/projects`, `/graph`, `/memory`, `/search`), backed by two local JSON files (`storage/anagrama-state.json` for the graph, `storage/memory.json` for memory) — no external database required to run it.
- A working, if simple, ingestion path: text/markdown/CSV/JSON upload → regex-based concept extraction → graph nodes/edges → searchable.
- A working chat/ask flow: `apps/web/app/page.tsx`'s input box really calls `POST /stream`, parses SSE events, and displays the streamed answer — with a graceful local-text fallback if the API is unreachable.
- Optional real-LLM answers via Gemini (`GEMINI_API_KEY`), with a configured fallback model on 404.
- Backend test coverage for the API shape and the ingestion pipeline (`backend/tests/`), runnable via `npm run api:test`.

## What's demo/mocked, not real, in the live frontend

- The dashboard's "in focus" inquiry, "knowledge pulse" numbers, "unresolved tension" card, "recent activity" list, and the "next actions" agenda are all **hardcoded arrays in `apps/web/app/page.tsx`** — not fetched from `/graph`, `/memory`, `/projects`, or `/search`.
- The **knowledge graph visualization** (`apps/web/components/knowledge-graph.tsx`) renders a fixed 7-node/10-edge dataset defined in the component itself — it does not call `GET /graph`.
- The greeting ("Good morning, Mira." / "Welcome back, Mira.") and the "Mira Chen" user badge are hardcoded — there's no auth/user system anywhere in the repo.
- Sidebar navigation items (Home/Knowledge/Projects/Research/Studio/Graph/Library) only toggle local `active` state — none of them route anywhere or change what's displayed beyond a label.

## Documentation vs. code: evidence of an undocumented rewrite, not just staleness

The pre-existing `docs/AGENT_ARCHITECTURE.md`, the prior `docs/ARCHITECTURE.md`, `docs/DEPLOYMENT.md`, and `README.md` all describe an **OpenAI Agents SDK** / **OpenAI Responses API** based orchestrator with real specialist agents and a `backend/agents/definitions.py` file. That file isn't on disk today, but `backend/agents/__pycache__/definitions.cpython-312.pyc` is — a `.pyc` only exists if Python actually compiled a real `definitions.py` at some point. So this most likely was built (matching the older docs) and then **replaced** by the current, much simpler `backend/agents/orchestrator.py` — one function that keyword-matches a specialist label and, if configured, calls **Gemini** (there is no OpenAI dependency in `apps/api/requirements.txt` at all). `docs/ARCHITECTURE.md` was rewritten in this pass to reflect the real code and to record this finding; the other docs listed above were left as-is (out of this task's scope) but should be treated as describing a **prior or planned implementation**, not the current one, until reconciled. This `__pycache__` evidence is gitignored and machine-local — it won't survive a fresh checkout, so it's worth confirming with whoever did the rewrite while it's still there.

## Two frontends, one dead

- `apps/web/` is the real, wired-up frontend (`npm run dev` → `next dev apps/web`).
- Root `app/page.tsx` + `src/` (a Zustand-based chat UI) is **not reachable via any `package.json` script**, and would fail to build if it were, since `src/store/app-store.ts` imports `zustand`, which isn't declared as a dependency anywhere in `package.json`. This reads as an earlier draft left in place after `apps/web` superseded it — **uncertain** whether it's intentionally kept for reference or simply not cleaned up.
- `src/lib/src/lib/projects.ts` and `src/lib/src/lib/upload.ts` sit under a doubled `src/lib/src/lib/` path — almost certainly a path mistake from however those files were generated or moved, rather than an intentional structure.

## Infrastructure gap

`docker-compose.yml` provisions Postgres+pgvector and Neo4j, and `.env.example`/`backend/config/settings.py` define connection variables for both (`DATABASE_URL`, `POSTGRES_URL`, `VECTOR_DB_URL`, `NEO4J_URI`, etc.) — but **no code in `backend/` actually opens a Postgres or Neo4j connection**. The graph and memory stores are both flat local JSON files. This matches what `docs/VALIDATION_CHECKLIST.md` already flags as open ("Configure PostgreSQL/pgvector and Neo4j, then run production-adapter integration tests"), so it appears to be a known, tracked gap rather than an oversight.

## Security/hygiene note

`.gitignore` lists `.env` but **not** `.env.local`. An untracked `.env.local` (68 bytes) currently sits at the repo root, unprotected by `.gitignore` — if a broad `git add`/`git add -A` is ever run in this project, that file would be staged. Its contents were not read as part of this pass. Recommend adding `.env*.local` (or at least `.env.local`) to `.gitignore` before it risks being committed.

## No CI, no `apps/api` app code, empty `scripts/`

- No CI configuration (GitHub Actions or otherwise) found.
- `apps/api/` contains only `requirements.txt` — despite the `apps/api` name suggesting a standalone API package, the real FastAPI app lives in the top-level `backend/` package. **Uncertain** whether `apps/api/` was meant to eventually house the backend and the move hasn't happened, or whether it's an intentional split (deps declared separately from code location).
- `scripts/` is an empty directory.

## Update (2026-07-19): real context-assembly + prompt-engineering layer added

Added `backend/agents/context.py` (`build_context()` — assembles graph nodes, matching sources, and recent memory into one structured object, replacing ad hoc string-building that used to live inline in the orchestrator) and `backend/prompts/specialists.py` (`build_system_prompt()` — a distinct, tailored system prompt per specialist, built on the shared `EXECUTIVE_INSTRUCTIONS` base). `backend/agents/orchestrator.py` was updated to use both. This is now real, not cosmetic: a live `/stream` call routed to "Planning" returned a Gemini answer that opened with "As the Planning Specialist for Anagrama, I have mapped out a concrete, relation-based plan..." — the specialist identity actually shapes the model's output now.

This is **not** the OpenAI Agents SDK multi-agent system the older docs describe — it's one Gemini call per turn with a context object and a specialist-selected prompt, not separate agents each making their own call. Verified: `backend/tests/test_agents.py` (4 new tests) plus the existing 4 all pass (8/8), and a live end-to-end `/stream` smoke test confirmed the new prompt actually reaches Gemini and changes its answer.

**New known gap this introduces**: `choose_specialist()` is still the same keyword `if/elif` matcher — the *quality* of specialist selection hasn't changed, only what happens once a specialist is chosen. A message that doesn't hit any of the keyword lists still silently falls through to "Knowledge."

## Net read

The backend's core loop (ingest → graph → retrieve → respond → remember) is real, tested, and runnable entirely locally with no external services, and as of the update above, its context-assembly and per-specialist prompting are real rather than cosmetic. The frontend layer built on top of it (`apps/web`) is still a polished visual design that is only partially wired to that backend — most of what's on screen is placeholder content dressing up a single working chat endpoint. The project's own documentation describes a more advanced, OpenAI-Agents-SDK-based *multi-agent* orchestration layer (separate agents, separate calls) that still has not been implemented; the gap between those docs and the code is still the single largest thing to reconcile before trusting `docs/AGENT_ARCHITECTURE.md`, `docs/DEPLOYMENT.md`, or `README.md` at face value.
