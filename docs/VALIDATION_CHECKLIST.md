# Validation checklist

- [x] Frontend uses App Router, responsive design, graph/evidence/action workspaces, and streaming UI.
- [x] FastAPI exposes health, chat, stream, upload, projects, graph, memory, and search routes.
- [x] Local ingestion updates graph and retrieval can use new source content.
- [x] Memory persists across process restarts through its adapter.
- [x] Stream contract emits tool, delta, and completion events.
- [ ] Configure `OPENAI_API_KEY`, then exercise the live Responses API call.
- [ ] Configure PostgreSQL/pgvector and Neo4j, then run production-adapter integration tests.
- [ ] Add PDF/DOCX/image/web/GitHub/YouTube parser adapters before claiming full file-format coverage.
