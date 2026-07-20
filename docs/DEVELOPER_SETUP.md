# Developer setup

1. Copy `.env.example` to `.env`, then provide `OPENAI_API_KEY` for live AI calls.
2. Install the API dependencies: `python -m pip install -r apps/api/requirements.txt`.
3. Run `npm run dev` for the web workspace at `http://localhost:3000`.
4. Run `npm run api:dev` for FastAPI at `http://localhost:8000`.
5. Run `npm run api:test` and `npm run build`.

With no API key the API remains fully usable in local deterministic mode: ingestion, graph updates, retrieval, memory persistence, and SSE event shapes are testable. `/health` reports the key status without exposing credentials.
