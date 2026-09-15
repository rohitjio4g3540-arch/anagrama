# Current Architecture

> This document describes the **current implementation state** of Anagrama as of 2026-09-09. It is based on a comprehensive technical audit of the codebase. For the target architecture and evolution plan, see [TARGET_ARCHITECTURE.md](TARGET_ARCHITECTURE.md).

## Overview

Anagrama is currently a functional prototype with a clean architectural foundation. It consists of a Next.js frontend, FastAPI backend, and local JSON-based storage. The system implements a working chat/ask flow with knowledge graph integration, but most dashboard UI elements are mocked.

## Technology Stack

### Frontend
- **Framework**: Next.js 16.2.10 with App Router
- **UI Library**: Custom components with Tailwind CSS v4
- **Animations**: Framer Motion
- **Location**: `apps/web/` directory
- **Status**: Functional, but dashboard largely mocked

### Backend
- **Framework**: FastAPI with Pydantic v2
- **Language**: Python 3.12
- **LLM Integration**: Google Gemini via `google-genai` SDK
- **Location**: `backend/` directory
- **Status**: Fully functional with comprehensive API routes

### Storage
- **Abstraction Layer**: Storage interface with JSON and PostgreSQL adapters
- **Active Backend**: JSON file-based storage (default)
- **Graph Data**: Local JSON file (`storage/anagrama-state.json`)
- **Memory Data**: Local JSON file (`storage/memory.json`)
- **File Storage**: Local filesystem (`storage/uploads/`)
- **PostgreSQL Schema**: Defined in `backend/migrations/schema.sql` (ready, not active)
- **Configuration**: `USE_POSTGRES` and `POSTGRES_URL` environment variables
- **Status**: JSON functional, PostgreSQL foundation ready, migration not yet executed

### Infrastructure
- **Containerization**: Docker Compose with PostgreSQL+pgvector and Neo4j (unused)
- **Deployment**: Vercel configuration present
- **Status**: Infrastructure scaffolded but not integrated

## Architecture Diagram (Current State)

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Next.js 16 App Router (apps/web/)                          │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │  Dashboard UI (page.tsx)                            │ │ │
│  │  │  ✓ Chat Input (wired to /stream)                     │ │ │
│  │  │  ✗ Knowledge Graph (mocked - fixed 7 nodes)          │ │ │
│  │  │  ✗ Recent Activity (mocked - hardcoded array)        │ │ │
│  │  │  ✗ Stats/Agenda (mocked - static values)             │ │ │
│  │  │  ✗ Navigation (inert - local state only)             │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/SSE
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          API Layer                                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  FastAPI (backend/main.py, backend/api/routes.py)           │ │
│  │  Routes: /health, /stream, /chat, /upload, /projects,      │ │
│  │         /graph, /memory, /search                             │ │
│  │  CORS: allow_origins=["*"] (all origins)                   │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Orchestration Layer                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Single Orchestrator Function (orchestrator.py)            │ │
│  │  ✓ Context Assembly (context.py)                           │ │
│  │  ✓ Specialist Selection (keyword-based if/elif)           │ │
│  │  ✓ Tool Event Emission (tool/handoff/delta/complete)        │ │
│  │  ✓ LLM Coordination (Gemini only)                         │ │
│  │  ✗ True Multi-Agent System (single function only)          │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌──────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   LLM Layer       │ │  Retrieval      │ │  Storage        │
│  ┌────────────┐  │ │  ┌───────────┐  │ │  ┌────────────┐ │
│  │ Gemini     │  │ │  │ Graph     │  │ │  │ Graph JSON │ │
│  │ Provider   │  │ │  │ Context   │  │ │  │ (local)    │ │
│  │ (google-  │  │ │  │ Search    │  │ │  └────────────┘ │
│  │  genai)    │  │ │  │ Memory    │  │ │  ┌────────────┐ │
│  │ gemini-2.5-│  │ │  │ (keyword  │  │ │  │ Memory     │ │
│  │ flash)     │  │ │  │  only)    │  │ │  │ JSON       │ │
│  └────────────┘  │ │  └───────────┘  │ │  │ (local)    │ │
│                  │ │                 │ │  └────────────┘ │
│  Fallback:       │ │                 │ │                 │
│  gemini-3.5-flash│ │                 │ │  No PostgreSQL  │
│                  │ │                 │ │  No Neo4j       │
└──────────────────┘ └─────────────────┘ └─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Ingestion Layer                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Pipeline (backend/ingestion/pipeline.py)                   │ │
│  │  ✓ Concept Extraction (regex word frequency)               │ │
│  │  ✓ Node/Edge Creation (document → concepts)                 │ │
│  │  ✓ Source Preservation (full content + metadata)           │ │
│  │  ✗ PDF/DOCX/image/web/GitHub/YouTube (TXT/MD/CSV/JSON only)│ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Component Detail

### Frontend Architecture

#### Live Implementation
- **Dashboard**: Single-page component with sidebar navigation (inert)
- **Chat Input**: Fully wired to `POST /stream` with SSE parsing
- **API Integration**: Real-time streaming with graceful fallback to local text
- **Responsive Design**: Mobile-responsive layout with Tailwind CSS
- **Animations**: Framer Motion for UI transitions and graph visualization

#### Mocked/Placeholder Elements
- **Knowledge Graph**: Fixed 7-node/10-edge SVG dataset (not from `/graph` endpoint)
- **Recent Activity**: Hardcoded source array
- **Stats Cards**: Animated but static values
- **Next Actions**: Hardcoded task/project/when tuples
- **User Profile**: Hardcoded "Mira Chen" with time-based greeting
- **Navigation**: Sidebar only sets local `active` state, no routing

#### Dead Code
- **Root Frontend**: `app/page.tsx` + `src/` directory exists but is unreachable
- **Missing Dependency**: Dead frontend imports `zustand` not in package.json
- **Path Error**: `src/lib/src/lib/` duplicate directory structure

### Backend Architecture

#### API Routes (<ref_file file="E:\fenric\New folder\anagrama\backend\api\routes.py" />)
- **GET /health**: Health check with service status and Gemini configuration
- **POST /stream**: SSE streaming chat endpoint (primary interaction)
- **POST /chat**: Non-streaming chat endpoint (returns concatenated response)
- **POST /upload**: File upload for ingestion (TXT/MD/CSV/JSON only)
- **GET /projects**: List all projects
- **POST /projects**: Create new project
- **GET /graph**: Get knowledge graph snapshot (nodes, edges, sources)
- **GET /memory**: Get memory entries (optionally filtered by project_id)
- **POST /memory**: Add memory entry
- **GET /search**: Search sources by keyword

#### Orchestrator (<ref_file file="E:\fenric\New folder\anagrama\backend\agents\orchestrator.py" />)
- **Single Function**: `run()` handles complete request lifecycle
- **Context Assembly**: Gathers graph nodes, sources, and memory via `build_context()`
- **Specialist Selection**: Keyword-based `if/elif` matching (6 specialists)
- **LLM Integration**: Calls Gemini with specialist-specific system prompt
- **Streaming**: Word-by-word streaming (not true token streaming)
- **Memory Recording**: Records user message (not AI response) to memory

#### Context Assembly (<ref_file file="E:\fenric\New folder\anagrama\backend\agents\context.py" />)
- **AssembledContext**: Structured bundle with message, project_id, nodes, sources, memories
- **Summaries**: Generated properties for source_summary, concept_summary, memory_summary
- **Citations**: Extracted from context for response attribution
- **Pattern**: Clean separation of retrieval logic from orchestrator

#### Specialist System (<ref_file file="E:\fenric\New folder\anagrama\backend\prompts\specialists.py" />)
- **6 Specialists**: Knowledge, Research, Writing, Planning, Design, Programming
- **System Prompts**: Distinct, tailored prompts per specialist
- **Selection**: Keyword-based (not LLM-based classification)
- **Effect**: Specialist identity shapes Gemini's actual output (verified)

### Storage Architecture

#### Graph Storage (<ref_file file="E:\fenric\New folder\anagrama\backend\graph\store.py" />)
- **Implementation**: `LocalKnowledgeGraph` class
- **Storage**: Single JSON file at `storage/anagrama-state.json`
- **Pattern**: Read-all/rewrite-all with thread locking
- **Data**: nodes, edges, sources, projects
- **Status**: Development adapter, explicitly documented as temporary

#### Memory Storage (<ref_file file="E:\fenric\New folder\anagrama\backend\memory\store.py" />)
- **Implementation**: `HierarchicalMemory` class
- **Storage**: Single JSON file at `storage/memory.json`
- **Pattern**: Read-all/rewrite-all
- **Tiers**: working, conversation, project, knowledge, personal
- **Status**: Development adapter, explicitly documented as temporary

#### Source Preservation
- **Immutable**: Sources never modified, only added
- **Full Content**: Complete source content preserved with metadata
- **Evidence Tracking**: Graph nodes maintain `source_ids` arrays
- **Attribution**: Edges include `evidence` array of source IDs

### Retrieval Architecture

#### Hybrid Retrieval (<ref_file file="E:\fenric\New folder\anagrama\backend\retrieval\hybrid.py" />)
- **Graph Context**: Keyword matching over node labels
- **Source Search**: Keyword substring matching over title + content
- **Memory Retrieval**: Last 5 memory entries for project
- **Scoring**: Simple term frequency scoring
- **Limitations**: No semantic search, no embeddings, no temporal weighting

### LLM Integration

#### Gemini Provider (<ref_file file="E:\fenric\New folder\anagrama\backend\llm\gemini.py" />)
- **SDK**: `google-genai`
- **Models**: gemini-2.5-flash (primary), gemini-3.5-flash (fallback)
- **Pattern**: Abstract `LLMProvider` interface
- **Fallback**: Automatic fallback on 404 errors
- **Streaming**: Implemented but not true token streaming

#### Abstraction Layer (<ref_file file="E:\fenric\New folder\anagrama\backend\llm\base.py" />)
- **Interface**: `LLMProvider` abstract base class
- **Methods**: `generate()`, `stream()`
- **Extensibility**: Designed for multiple providers
- **Current**: Only Gemini implemented

### Ingestion Pipeline

#### Pipeline (<ref_file file="E:\fenric\New folder\anagrama\backend\ingestion\pipeline.py" />)
- **Concept Extraction**: Regex word-frequency ranking (words ≥4 letters)
- **Stopwords**: Small hardcoded stopword list
- **Limit**: Top 10 concepts per document
- **Document Node**: Creates document node with source reference
- **Edge Creation**: Up to 6 "discusses" edges from document to concepts
- **File Formats**: TXT, MD, CSV, JSON only (no PDF/DOCX/images)

### Data Models

#### Source Model
- **Fields**: id, title, kind, content, created_at, metadata
- **Kinds**: note, document, file
- **Immutability**: Never modified after creation

#### Graph Node Model
- **Fields**: id, label, type, confidence, source_ids
- **Types**: concept, entity, person, organization, document, project, conversation
- **Attribution**: source_ids array for provenance

#### Graph Edge Model
- **Fields**: id, source, target, relation, confidence, evidence
- **Evidence**: Array of source IDs supporting the relationship

#### Memory Model
- **Fields**: id, tier, content, project_id, created_at
- **Tiers**: working, conversation, project, knowledge, personal
- **Scope**: Can be filtered by project_id

## Current Limitations

### Storage Limitations
- **Scalability**: JSON read-all/rewrite-all won't scale
- **Concurrency**: Thread locking insufficient for production
- **Querying**: No complex query capabilities
- **Transactions**: No ACID guarantees

### Retrieval Limitations
- **Search Quality**: Keyword-only, no semantic understanding
- **Ranking**: Simple term frequency, no relevance scoring
- **Context**: Last-N memory, no temporal weighting
- **Personalization**: No user preference signals

### Orchestration Limitations
- **Specialist Selection**: Keyword-based, not intent understanding
- **Multi-Agent**: Single function, no true agent handoff
- **Scope Control**: No permission system or boundaries
- **Verification**: No result validation or confirmation

### Frontend Limitations
- **Data Integration**: 90% of dashboard is mocked
- **User Management**: No authentication or user profiles
- **Navigation**: No routing or view switching
- **Real-time Updates**: No live data updates

### Ingestion Limitations
- **File Formats**: Limited to text-based formats
- **Extraction**: Regex-based, no ML/LLM extraction
- **Chunking**: Only count, not actual chunking
- **Web/GitHub**: No web scraping or repository integration

## Technical Debt

### Documentation Debt
- **Stale Docs**: Multiple docs describe removed OpenAI/Agents-SDK system
- **Evidence**: `backend/agents/__pycache__/definitions.cpython-312.pyc` proves removed code
- **Impact**: Confusing for developers, misrepresents current state

### Code Quality Debt
- **Test Isolation**: Tests mutate persistent storage without cleanup
- **Deprecation Warnings**: FastAPI `@app.on_event` and Pydantic `datetime.utcnow()`
- **ESLint Configuration**: Ignore glob bug causing 735 false errors
- **Dead Code**: Root `app/` + `src/` directory unreachable

### Infrastructure Debt
- **Unused Infrastructure**: Docker Compose provisions databases not used
- **Environment Variables**: Many defined but not read by code
- **CORS**: Over-permissive (all origins allowed)
- **No CI/CD**: No automated testing or deployment pipeline

## Security Considerations

### Current Security Posture
- **Authentication**: None (no user management)
- **Authorization**: None (no permission system)
- **Input Validation**: Limited (basic Pydantic validation)
- **Secrets Management**: `.env.local` recently added to gitignore
- **CORS**: Allows all origins (security risk)

### Security Gaps
- **No Rate Limiting**: Unlimited API calls possible
- **No Input Sanitization**: Limited validation on file uploads
- **No Audit Logging**: No tracking of user actions
- **No Encryption**: Data stored in plain text
- **No Backup Strategy**: No automated backups

## Performance Characteristics

### Storage Performance
- **Read Latency**: JSON file read (filesystem dependent)
- **Write Latency**: Full file rewrite (scales poorly with data size)
- **Concurrency**: Thread locking (single-machine only)
- **Memory Usage**: Full dataset in memory (not scalable)

### API Performance
- **Response Time**: LLM-dependent (Gemini API latency)
- **Streaming**: Word-by-word (not true token streaming)
- **Retrieval**: Keyword matching (fast but limited)
- **Concurrency**: FastAPI async (good concurrency support)

### Frontend Performance
- **Bundle Size**: Next.js optimized (reasonable)
- **Rendering**: Client-side rendering (initial load time)
- **Animations**: Framer Motion (smooth but CPU-intensive)
- **Data Loading**: No real data loading (mocked data)

## Known Issues

### Critical Issues
1. **Dashboard Mock Data**: UI doesn't reflect real backend state
2. **Documentation Mismatch**: Docs describe removed OpenAI system
3. **JSON Storage**: Won't scale for production use
4. **No Authentication**: No user management or access control

### High Priority Issues
1. **Test Isolation**: Tests pollute persistent storage
2. **Dead Frontend Code**: Unreachable code cluttering repository
3. **Missing File Formats**: No PDF/DOCX/image/web support
4. **No Permission System**: No access control or authorization

### Medium Priority Issues
1. **Keyword Search Only**: No semantic search capabilities
2. **Specialist Selection**: Simplistic keyword matching
3. **No True Multi-Agent**: Single orchestrator function
4. **ESLint Configuration**: Broken ignore globs

### Low Priority Issues
1. **Deprecation Warnings**: FastAPI and Pydantic deprecations
2. **CORS Over-Permissive**: Security risk but low impact currently
3. **Workspace Warning**: Next.js workspace root warning
4. **Empty Directories**: `backend/tools/` and `backend/services/` empty

## Testing Status

### Test Coverage
- **API Tests**: Basic route testing in `backend/tests/test_api.py`
- **Agent Tests**: Context and specialist testing in `backend/tests/test_agents.py`
- **Pipeline Tests**: Ingestion and retrieval testing in `backend/tests/test_pipeline.py`
- **Frontend Tests**: None

### Test Quality
- **Isolation**: Poor (tests mutate persistent storage)
- **Coverage**: Limited to happy paths
- **Frontend**: No automated testing
- **Integration**: Limited integration testing

## Deployment Status

### Current Deployment
- **Frontend**: Vercel configuration present
- **Backend**: No production deployment configuration
- **Database**: No production database configuration
- **Infrastructure**: Docker Compose for local development only

### Deployment Readiness
- **Environment Variables**: Partially configured
- **Secrets Management**: Basic (env files)
- **Monitoring**: None
- **Logging**: Basic Python logging
- **Backups**: None

## Summary

The current architecture provides a solid foundation with clean separation of concerns and well-designed patterns. The FastAPI backend is functional and extensible, the Next.js frontend is polished but largely mocked, and the storage system works for development but needs production migration.

**Strengths:**
- Clean architectural separation (frontend/backend/storage)
- Working core loop (ingest → retrieve → respond → remember)
- Good data models with source preservation
- Abstract LLM provider interface
- Effective context assembly pattern
- SSE streaming architecture

**Critical Gaps:**
- Dashboard UI is 90% mocked
- No production storage (JSON only)
- No semantic search (keyword only)
- No authentication or user management
- Documentation describes removed system

**Overall Assessment:** Functional prototype with excellent architectural patterns but significant implementation gaps before production readiness.
