# Anagrama

Anagrama is an AI-native Knowledge Operating System: a place to capture information, preserve evidence, connect concepts, and reason across what you know. The interface is intentionally an editorial workspace—not a chat-first product. It foregrounds inquiries, graph context, tensions, sources, and forward motion.

## What runs today

- Premium responsive Next.js App Router workspace in `apps/web`
- FastAPI API with documented `/health`, `/chat`, `/stream`, `/upload`, `/projects`, `/graph`, `/memory`, and `/search` routes
- One mandatory ingestion path with source provenance, concept extraction, graph edges, retrieval, and memory updates
- Local persistent development adapters (JSON files), SSE streaming, and specialist routing
- Current Gemini integration when an API key is configured; single orchestrator with specialist-specific prompts

## Run it

```powershell
Copy-Item .env.example .env
python -m pip install -r apps/api/requirements.txt
npm run dev
# another terminal
npm run api:dev
```

Open `http://localhost:3000`. The API docs are at `http://localhost:8000/docs`.

## Repository map

```text
apps/web/       Next.js product workspace
apps/api/       Python dependency manifest
backend/        API, agents, graph, memory, ingestion, retrieval, services
storage/        local development object/state storage
docs/           operating and architecture documentation
```

## Documentation

- [Current Architecture](docs/CURRENT_ARCHITECTURE.md) - Implementation state as of 2026-09-09
- [Target Architecture](docs/TARGET_ARCHITECTURE.md) - Planned evolution to Personal Intelligence System
- [Architecture Decisions](docs/ARCHITECTURE_DECISIONS.md) - Architectural decision records
- [Concepts](docs/CONCEPTS.md) - Key conceptual systems and boundaries
- [Roadmap](docs/ROADMAP.md) - Phased implementation plan
- [Architecture](docs/ARCHITECTURE.md) - Detailed current architecture
- [Memory Architecture](docs/MEMORY_ARCHITECTURE.md) - Memory system design
- [Knowledge Graph](docs/KNOWLEDGE_GRAPH.md) - Knowledge graph design
- [Validation Checklist](docs/VALIDATION_CHECKLIST.md) - Production rollout boundaries
