# Deployment guide

Deploy the web app and API independently. In production, set `DATABASE_URL`/`POSTGRES_URL` to PostgreSQL with pgvector, configure Neo4j credentials, and point `ANAGRAMA_STORAGE_PATH` to an object-store adapter. Keep `OPENAI_API_KEY` secret-managed; do not expose it through `NEXT_PUBLIC_*` variables.

Terminate TLS before the API, allow the web origin in CORS, and preserve `text/event-stream` buffering headers at the proxy. Send traces and structured logs from agent runs, tool runs, retrieval, graph writes, memory writes, latency, and failures to your observability provider.
