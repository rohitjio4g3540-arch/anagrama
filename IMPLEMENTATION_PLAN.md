# IMPLEMENTATION_PLAN.md

> Generated 2026-07-19 from `docs/PROJECT.md`, `docs/ARCHITECTURE.md`, `context/repository_map.md`, `context/current_state.md`, and a fresh read of the full repository — plus **actual build/test/runtime verification** (not just static reading). No code was modified to produce this plan; the only changes made so far were corrections to the four doc files themselves (see "Step 1 fixes" below).

## Step 1 fixes already applied (before this plan was written)

While re-checking the generated docs for mistakes, found `backend/agents/__pycache__/definitions.cpython-312.pyc` on disk — proof that `backend/agents/definitions.py` (an OpenAI-Agents-SDK-based orchestrator, matching what `docs/AGENT_ARCHITECTURE.md` describes) existed and ran at some point, before being replaced by the current, simpler `backend/agents/orchestrator.py` (Gemini-only, keyword-matched specialist labels). The original framing in `docs/PROJECT.md`, `docs/ARCHITECTURE.md`, and `context/current_state.md` — "the docs describe an aspirational design that was never built" — was corrected to: **this was likely a real implementation that got rewritten, and the docs were never updated for the rewrite.** This is a materially different (and more concerning) finding: it means `docs/AGENT_ARCHITECTURE.md`, `docs/DEPLOYMENT.md`, and `README.md` are not just ahead-of-code aspiration, they're describing a **previous, removed system** as if it were current.

## Verification performed for this plan

| Check | Command | Result |
|---|---|---|
| Frontend build | `npm run build` | ✅ Succeeds. TypeScript passes. Static pages generated. One benign warning: ambiguous workspace root (see P2 below). |
| Backend boot | `.venv/Scripts/python.exe -m uvicorn backend.main:app --port 8000` | ✅ Clean startup, no errors. |
| Backend health | `GET /health` | ✅ `{"status":"ok","services":"anagrama","gemini_configured":true,"graph_adapter":"local"}` — **a real `GEMINI_API_KEY` is configured in this environment**, so the LLM path is actually live, not just theoretically wired. |
| Backend reads | `GET /graph`, `GET /projects` | ✅ Both respond correctly with real (if sparse) local data. |
| Backend tests | `python -m pytest backend/tests -q` | ✅ 4/4 pass. Only deprecation warnings (see P2). ⚠️ **But this run added duplicate "Attention study" entries to the persistent `storage/anagrama-state.json`** — confirmed by inspecting `/graph` before/after. Tests are not isolated from local dev/demo storage. |
| Frontend lint | `npm run lint` | ⚠️ Reported **735 errors / 12116 warnings** — alarming number, but nearly all of it is `eslint` linting **`apps/web/.next/` build output** (minified Turbopack bundles, generated `.d.ts` files) because the root `eslint.config.mjs`'s `globalIgnores(['.next/**', ...])` doesn't match `apps/web/.next/**` when eslint is invoked as `eslint apps/web`. Once you exclude everything under `.next/`, the real signal on hand-written code is **one warning**: `apps/web/app/page.tsx:29` — use `next/image` instead of `<img>`. |

## Broken or incomplete features

Ranked roughly by how much they'd matter to someone evaluating the product, highest first.

1. **The dashboard is almost entirely mocked.** In `apps/web/app/page.tsx`: the "in focus" inquiry, "knowledge pulse" number, "unresolved tension" card, "recent activity" list, and "next actions" agenda are hardcoded arrays in the component. `components/knowledge-graph.tsx` renders a fixed 7-node/10-edge dataset, not `GET /graph`'s actual response (which — per the verification above — already has real data in it). **Only the chat/ask input is wired to a real endpoint.**
2. **Sidebar navigation is inert.** Clicking Home/Knowledge/Projects/Research/Studio/Graph/Library only sets a local `active` label; nothing routes or changes what's rendered.
3. ~~**"Specialist handoff" is cosmetic.**~~ **RESOLVED 2026-07-19.** `choose_specialist()` is still a keyword `if/elif`, but each specialist now gets a distinct, tested system prompt (`backend/prompts/specialists.py`) built against a real context-assembly object (`backend/agents/context.py`), and this measurably changes Gemini's actual output (verified live). Still not a full multi-agent system (one Gemini call per turn, not one per specialist) — see `docs/ARCHITECTURE.md`'s Orchestrator section for the current, accurate description.
4. **A second, dead frontend exists at the repo root** (`app/page.tsx` + `src/`). Not reachable via any npm script, and would fail to build anyway — `src/store/app-store.ts` imports `zustand`, which isn't in `package.json`.
5. **ESLint is currently useless as a CI gate** due to the ignore-glob bug described above (735 false-positive errors bury the one real warning).
6. **Tests mutate persistent local storage with no isolation** — confirmed above. Every `pytest` run adds another duplicate "Attention study" source/node/edge set to `storage/anagrama-state.json` and writes to `storage/memory.json`.
7. **`.env.local` is not covered by `.gitignore`** (only `.env` is listed). A real local secrets file currently sits un-ignored at the repo root.
8. **Stale docs describing a removed OpenAI/Agents-SDK system** (`docs/AGENT_ARCHITECTURE.md`, `docs/DEPLOYMENT.md` — mentions `OPENAI_API_KEY`, which doesn't exist in this codebase — and `README.md`'s "Current OpenAI Responses API integration" line).
9. **No production storage adapters.** `docker-compose.yml` provisions Postgres+pgvector and Neo4j, and env vars exist for both, but no code path in `backend/` opens either connection — everything is flat local JSON. (This is already tracked as an open item in `docs/VALIDATION_CHECKLIST.md`, so it's a known gap, not a surprise.)
10. **Upload only accepts `.txt`/`.md`/`.csv`/`.json`** — no PDF/DOCX/image/web/GitHub/YouTube ingestion (also already flagged in `docs/VALIDATION_CHECKLIST.md`).
11. **FastAPI/Pydantic deprecation warnings**: `@app.on_event("startup")` (FastAPI wants lifespan handlers now) and `datetime.utcnow()` in `backend/models/schemas.py` (Pydantic/Python want timezone-aware datetimes). Not failing today, but will break on a future dependency bump.
12. **Next.js build warning**: a `pnpm-lock.yaml` at `C:\Users\DELL\` (one level above `Downloads`) plus this project's own `package-lock.json` makes Next.js guess the wrong workspace root. Cosmetic today (build still succeeds), but worth silencing.
13. **`apps/api/` is an empty shell** (only `requirements.txt`) despite implying a standalone API package — the real FastAPI app lives in top-level `backend/`. Unclear if this is intentional or an unfinished move.
14. **CORS is hardcoded to `http://localhost:3000` only** (`backend/main.py`) — will reject requests from any other origin, including a deployed demo URL.
15. **`docs/TOOL_DEVELOPMENT.md` references `backend/tools/`, which doesn't exist.** No tools have been built in that pattern yet.

## Priority ranking (highest → lowest impact)

### P0 — fix first, cheap and/or risk-reducing
- Fix the `eslint.config.mjs` ignore globs so `.next/**` actually matches `apps/web/.next/**` (or switch to `**/.next/**`). Restores lint as a usable signal.
- Add `.env.local` (and ideally `.env*.local`) to `.gitignore`. Prevents an accidental secret commit.
- Decide whether the mocked dashboard content is acceptable for your immediate goal, or needs to be wired to real data — this is the single biggest "is this real" risk and should be decided before more UI work is done on top of it.

### P1 — high impact, moderate effort
- Isolate test storage from dev/demo storage (e.g., point `Settings.state_path`/memory path at a temp dir during `pytest`, or add fixtures that snapshot/restore `storage/*.json`). Stops tests from silently corrupting demo data.
- Add a visible note (or reconcile outright) in `docs/AGENT_ARCHITECTURE.md`, `docs/DEPLOYMENT.md`, and `README.md` that the OpenAI/Agents-SDK description is stale and the real system uses Gemini via a single orchestrator function — so nobody demos or promises a capability that isn't there.
- Decide the fate of the dead root `app/`+`src/` frontend: delete it, or leave a clear marker (e.g. a `NOT_USED.md`) so it doesn't get mistaken for live code.

### P2 — polish, do once P0/P1 are settled
- Wire at least the knowledge-graph panel and recent-activity list to real `/graph`/`/search` data (if P0's decision was "make it real").
- Swap `<img>` for `next/image` in `apps/web/app/page.tsx`.
- Migrate `@app.on_event("startup")` to a lifespan handler; fix `datetime.utcnow()` deprecation.
- Fix the Next.js workspace-root warning (`turbopack.root` in `apps/web/next.config.ts`, or remove/ignore the stray lockfile).

### P3 — defer unless there's a specific reason to prioritize them
- Real Postgres/pgvector + Neo4j adapters (currently local JSON only, and that's fine for local dev/demo).
- Additional ingestion formats (PDF/DOCX/images/web/GitHub/YouTube).
- CORS beyond `localhost:3000` (only matters once there's a real second origin to serve).
- Actual per-specialist agent logic (only matters if "specialist handoff" needs to be a real, demoable capability rather than a labeled response).

## Milestones

> Note: this reorders the milestone skeleton you sketched, because verification above shows **Milestone 1's "frontend runs / backend runs / API connection / chat endpoint" is already true today** — re-litigating it would waste time. The milestones below start from actual current state.

### Milestone 1 — Trust the plumbing, close the two cheap gaps
- [x] Frontend builds (`npm run build`) — verified
- [x] Backend runs (`uvicorn`) — verified
- [x] API connection works (`/health`, `/graph`, `/projects`) — verified
- [x] Chat endpoint works (`/stream`, real Gemini call, key configured) — verified
- [ ] Fix ESLint ignore-glob bug
- [ ] Add `.env.local` to `.gitignore`
- **Dependencies**: none — everything here is either already done or a standalone config fix.
- **Blockers**: none.

### Milestone 2 — Make the demo honestly reflect what the backend can do
- [ ] Decide: wire the dashboard's mocked panels to real data, or keep them as clearly-labeled demo content
- [ ] (If wiring) connect knowledge-graph panel to `GET /graph`
- [ ] (If wiring) connect recent-activity list to `GET /search` or ingested sources
- **Dependencies**: needs Milestone 1's API layer (already verified working).
- **Blockers**: this needs a product decision from you first — how much of the polished mock UI is worth making real vs. how much time you have. Flagging as a decision blocker, not an engineering one.

### Milestone 3 — Data integrity and documentation truthfulness
- [ ] Isolate test storage so `pytest` stops polluting `storage/*.json`
- [ ] Reconcile or clearly flag the stale OpenAI/Agents-SDK docs (`AGENT_ARCHITECTURE.md`, `DEPLOYMENT.md`, `README.md`)
- [ ] Decide fate of the dead root `app/`+`src/` frontend
- **Dependencies**: none — can run fully in parallel with Milestone 2.
- **Blockers**: none, purely engineering + doc-writing time.

### Milestone 4 — Polish, correctness debt, deployment readiness
- [ ] `next/image` swap, FastAPI lifespan migration, `datetime.utcnow()` fix
- [ ] Fix Next.js workspace-root warning
- [ ] CORS beyond `localhost:3000` if/when there's a deployed origin
- [ ] (Deferred, optional) Postgres/pgvector + Neo4j adapters, additional ingestion formats, real specialist logic
- **Dependencies**: meaningfully follows Milestone 2's decision (what's real determines what needs to be fast/deployed/correct).
- **Blockers**: none technical; sequencing depends on how much of P3 you actually want before a deadline.

## Summary of blockers requiring your decision (not pure engineering work)

1. Is the mocked dashboard content acceptable for your goal, or does it need to become real? (Drives all of Milestone 2.)
2. Should the OpenAI/Agents-SDK docs be rewritten to match Gemini reality, or kept as a "future direction" note? (Low effort either way, but it's a call about what you want the docs to promise.)
3. Delete or keep the dead root `app/`+`src/` frontend?

No code has been modified as part of this plan (only the four doc files were corrected in the Step 1 pass, per your instruction to fix inaccuracies before moving on).
