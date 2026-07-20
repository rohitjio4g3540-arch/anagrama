# repository_map.md

> One line per source file in `anagrama`, as of 2026-07-19. Excludes `node_modules/`, `.venv/`, `__pycache__/`, `.pytest_cache/`, `.next/`, and `storage/` contents.

## Root

| File | Purpose |
|---|---|
| `README.md` | Project pitch + run instructions; links out to `docs/DEVELOPER_SETUP.md`, `docs/ARCHITECTURE.md`, `docs/VALIDATION_CHECKLIST.md` |
| `package.json` | Single root manifest; scripts drive both the Next.js app (`next dev/build/start apps/web`) and the FastAPI app (`api:dev`, `api:test`) |
| `package-lock.json` | npm lockfile |
| `tsconfig.json` | Shared TS config (`@/*` → repo root); extended by `apps/web/tsconfig.json` |
| `eslint.config.mjs` | ESLint flat config (Next core-web-vitals + typescript) |
| `postcss.config.mjs` | Wires in `@tailwindcss/postcss` |
| `docker-compose.yml` | Local Postgres+pgvector and Neo4j containers — **not yet connected to by any app code** (see ARCHITECTURE.md) |
| `.env.example` | Documents `GEMINI_*`, `DATABASE_URL`/`POSTGRES_URL`/`VECTOR_DB_URL`, `NEO4J_*`, `ANAGRAMA_STORAGE_PATH`, `NEXT_PUBLIC_API_URL` |
| `.env.local` | **Untracked, real local env file — not covered by `.gitignore`** (only `.env` is listed); not read as part of this pass |
| `.gitignore` | Ignores `node_modules/`, `.next/`, `.venv/`, `__pycache__/`, `.pytest_cache/`, `.env`, `storage/uploads/`, `storage/*.json`, `*.pyc` |

## `docs/` (pre-existing, hand-authored — not modified by this pass except `ARCHITECTURE.md`)

| File | Purpose | Note |
|---|---|---|
| `docs/ARCHITECTURE.md` | Rewritten in this pass to match actual code | See discrepancy section inside |
| `docs/PROJECT.md` | New — added in this pass | |
| `docs/AGENT_ARCHITECTURE.md` | Describes an OpenAI-Agents-SDK-based orchestrator | **Does not match current code** — see `docs/ARCHITECTURE.md` |
| `docs/DEPLOYMENT.md` | Deployment guidance, mentions `OPENAI_API_KEY` | That variable isn't used anywhere in the current codebase |
| `docs/DEVELOPER_SETUP.md` | Local setup steps | Broadly accurate; mentions `OPENAI_API_KEY` for "live AI calls" which is actually `GEMINI_API_KEY` in code |
| `docs/KNOWLEDGE_GRAPH.md` | Describes the graph data model and ingestion-as-only-write-path | Matches code |
| `docs/MEMORY_ARCHITECTURE.md` | Describes the tiered memory model | Matches code (tiers exist as a `Literal` type; nothing enforces tier-specific retrieval behavior beyond a flat list) |
| `docs/TOOL_DEVELOPMENT.md` | Guidance for adding tools | Aspirational — no `backend/tools/` directory exists yet despite being referenced |
| `docs/VALIDATION_CHECKLIST.md` | Checklist of done/open items | Consistent with what this pass found in code |

## `apps/`

| File | Purpose |
|---|---|
| `apps/api/requirements.txt` | Python dependencies for the FastAPI backend (no other files in `apps/api/` — the actual backend package lives in top-level `backend/`) |
| `apps/web/app/layout.tsx` | Root layout: fonts (Geist, Geist Mono, Fraunces), page metadata, favicon |
| `apps/web/app/page.tsx` | The live product page — dashboard UI + chat/ask input wired to `POST /stream` |
| `apps/web/app/globals.css` | Tailwind v4 entrypoint + CSS variables + noise/grid background utility classes |
| `apps/web/components/knowledge-graph.tsx` | Hardcoded-data SVG graph visualization (hover/focus interactions via Framer Motion) |
| `apps/web/components/ui/button.tsx` | Minimal styled `<button>` wrapper |
| `apps/web/components/ui/card.tsx` | Minimal styled `<div>` wrapper |
| `apps/web/next.config.ts` | Sets `reactStrictMode: true` |
| `apps/web/tsconfig.json` | Extends root `tsconfig.json` |
| `apps/web/next-env.d.ts` | Next.js-generated, not hand-written |
| `apps/web/public/logo.png` | App logo/favicon image |

## `backend/` (FastAPI app, Python package)

| File | Purpose |
|---|---|
| `backend/__init__.py` | Package docstring only |
| `backend/main.py` | FastAPI app instance, CORS (locked to `http://localhost:3000`), router mount, startup hook that loads settings |
| `backend/api/routes.py` | All HTTP routes: `/health`, `/stream`, `/chat`, `/upload`, `/projects` (GET/POST), `/graph`, `/memory` (GET/POST), `/search` |
| `backend/agents/orchestrator.py` | The single `run()` generator: retrieval → memory → specialist-label selection (keyword match) → optional Gemini call → streamed answer → memory write → completion event |
| `backend/config/settings.py` | Pydantic `Settings` loaded from `.env`/`.env.local`; `lru_cache`d `get_settings()` |
| `backend/llm/__init__.py` | `get_llm()` factory — returns a `GeminiProvider` if `GEMINI_API_KEY` is set, else `None` |
| `backend/llm/base.py` | `LLMProvider` abstract base (`generate`, `stream`) — docstring name-checks Gemini/OpenAI/Ollama/Anthropic/Groq/OpenRouter, but **only Gemini is implemented** |
| `backend/llm/gemini.py` | `GeminiProvider` — wraps `google.genai`, with a fallback model on `ClientError` 404 |
| `backend/graph/store.py` | `LocalKnowledgeGraph` — JSON-file-backed nodes/edges/sources/projects, thread-locked, full-file rewrite on every write |
| `backend/ingestion/pipeline.py` | `ingest()`/`ingest_file()` — regex word-frequency "concept extraction", creates document + concept graph nodes and `discusses` edges |
| `backend/memory/store.py` | `HierarchicalMemory` — JSON-file-backed list of memory items, filterable by `project_id` |
| `backend/models/schemas.py` | Pydantic models: `Source`, `GraphNode`, `GraphEdge`, `Memory`, `ChatRequest`, `ProjectRequest`, `SearchResult` |
| `backend/prompts/executive.py` | The one system prompt used for the Gemini call |
| `backend/retrieval/hybrid.py` | `search()` (substring/term-overlap scoring over stored sources) and `graph_context()` (term match over stored node labels) |
| `backend/utils/ids.py` | `new_id(prefix)` — `prefix_<12 hex chars>` |
| `backend/tests/test_api.py` | Tests `/health` shape and that `/stream` emits `tool`/`delta`/`complete` events |
| `backend/tests/test_pipeline.py` | Tests concept extraction determinism and that ingestion updates the graph + is searchable |

**Directories referenced in prose docs but not present in code**: `backend/tools/` (referenced by `docs/TOOL_DEVELOPMENT.md`), `backend/agents/definitions.py` (referenced by `docs/AGENT_ARCHITECTURE.md`).

## Root `app/` + `src/` — orphaned second frontend (not wired into any script)

| File | Purpose |
|---|---|
| `app/page.tsx` | Renders `<ChatPanel />` — the entire page |
| `src/components/chat/chat-panel.tsx` | Bare-bones chat UI (unstyled), uses the Zustand store below |
| `src/store/app-store.ts` | Zustand store for chat messages/streaming state — **`zustand` is not in `package.json`**, so this would fail to build if ever entered |
| `src/lib/api.ts` | `apiFetch()` helper, `API_URL` from `NEXT_PUBLIC_API_URL` |
| `src/lib/stream.ts` | SSE-parsing `streamChat()` — same shape as the logic duplicated inline in `apps/web/app/page.tsx` |
| `src/lib/types.ts` | Shared `ChatRequest`/`StreamEvent`/`Citation` types for this orphaned frontend |
| `src/lib/generated/api-types.ts` | `openapi-typescript`-generated types from the FastAPI schema — accurate reference for the real API surface regardless of which frontend uses it |
| `src/lib/src/lib/projects.ts` | `getProjects()` — note the doubled `src/lib/src/lib/` path, almost certainly an accidental nesting bug |
| `src/lib/src/lib/upload.ts` | `uploadFile()` — same doubled-path anomaly |

## `scripts/`

Empty directory — no files present.
