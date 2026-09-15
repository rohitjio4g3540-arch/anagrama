# Target Architecture

> This document describes the **target architecture** for Anagrama as a Personal Intelligence System. It represents the planned evolution from the current state documented in [CURRENT_ARCHITECTURE.md](CURRENT_ARCHITECTURE.md). Implementation is phased as described in [ROADMAP.md](ROADMAP.md).

## Vision Statement

Anagrama will become a persistent, user-guided Personal Intelligence System that helps preserve and organize knowledge, conversations, ideas, projects, decisions, original sources, goals, context, and explicitly provided preferences and principles.

The system will help interpret the user's broader intent and assemble appropriate context for AI models and tools, prioritizing continuity, provenance, user control, and preventing important information from being silently lost.

**Core Principle:** Important information should be persistently preserved, attributable, addressable, and retrievable independently of any individual LLM context window.

## Architecture Overview

The target architecture builds on the current foundation while adding production-ready storage, semantic retrieval, intent understanding, and controlled execution.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface Layer                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Next.js Dashboard (real backend data integration)          │ │
│  │  - Knowledge graph visualization (real data)               │ │
│  │  - Project and activity dashboards                         │ │
│  │  - Memory curation interface                               │ │
│  │  - Skill and tool management                               │ │
│  │  - Permission and confirmation UI                           │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/SSE/WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          API Layer                                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  FastAPI with enhanced routes                               │ │
│  │  - Intent interpretation endpoints                         │ │
│  │  - Task contract management                                │ │
│  │  - Permission enforcement                                   │ │
│  │  - Skill and tool invocation                               │ │
│  │  - Verification and confirmation                           │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Central Orchestrator                           │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Intent Understanding                                       │ │
│  │  - User intent classification                              │ │
│  │  - Ambiguity detection                                     │ │
│  │  - Clarification request generation                        │ │
│  │                                                            │ │
│  │  Context Assembly Engine                                    │ │
│  │  - Enhanced AssembledContext pattern                       │ │
│  │  - Hybrid retrieval (keyword + semantic + structured)      │ │
│  │  - Temporal relevance weighting                            │ │
│  │  - User preference integration                            │ │
│  │                                                            │ │
│  │  Scope Control & Permissions                               │ │
│  │  - Task contract validation                                │ │
│  │  - Permission checking                                     │ │
│  │  - Boundary enforcement                                    │ │
│  │                                                            │ │
│  │  Execution Coordination                                    │ │
│  │  - Specialist/worker invocation                            │ │
│  │  - Tool execution coordination                             │ │
│  │  - Result aggregation                                     │ │
│  │                                                            │ │
│  │  Verification & Confirmation                               │ │
│  │  - Result validation                                       │ │
│  │  - Consequential action confirmation                       │ │
│  │  - Execution verification                                  │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌──────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Model Providers  │ │  Retrieval      │ │  Storage        │
│  ┌────────────┐  │ │  ┌───────────┐  │ │  ┌────────────┐ │
│  │ Gemini     │  │ │  │ Keyword   │  │ │  │ PostgreSQL  │ │
│  │ OpenAI     │  │ │  │ Search    │  │ │  │ + pgvector │ │
│  │ Anthropic  │  │ │  │           │  │ │  │            │ │
│  │ Local      │  │ │  │ Semantic  │  │ │  │ Tables:    │ │
│  │ (Ollama)   │  │ │  │ Search    │  │ │  │ - sources  │ │
│  └────────────┘  │ │  │ (pgvector)│  │ │  │ - nodes     │ │
│                  │ │  └───────────┘  │ │  │ - edges     │ │
│  Abstraction:    │ │                 │ │  │ - memories  │ │
│  LLMProvider     │ │  ┌───────────┐  │ │  │ - projects  │ │
│  Interface       │ │  │ Structured│  │ │  │ - decisions │ │
│                  │ │  │ Context   │  │ │  │ - tasks     │ │
│                  │ │  │ Filter    │  │ │  │ - skills    │ │
│                  │ │  └───────────┘  │ │  │ - tools     │ │
│                  │ │                 │ │  │ - users     │ │
│                  │ │  ┌───────────┐  │ │  └────────────┘ │
│                  │ │  │ Temporal  │  │ │                 │
│                  │ │  │ Weighting │  │ │  Features:     │ │
│                  │ │  └───────────┘  │ │  - ACID        │ │
│                  │ │                 │ │  - Indexing    │ │
│                  │ │  ┌───────────┐  │ │  - Backups     │ │
│                  │ │  │ User      │  │ │  - Migrations  │ │
│                  │ │  │ Curation  │  │ │                 │ │
│                  │ │  └───────────┘  │ │                 │ │
└──────────────────┘ └─────────────────┘ └─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Specialized Systems                            │
│  ┌─────────────────────┐  ┌─────────────────────┐             │
│  │  Skills System      │  │  Tools System       │             │
│  │  - Skill definitions │  │  - Tool registry    │             │
│  │  - Versioning        │  │  - Permission checks │             │
│  │  - Composition       │  │  - Execution logs    │             │
│  │  - Application       │  │  - Safety bounds     │             │
│  └─────────────────────┘  └─────────────────────┘             │
│                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────┐             │
│  │  Bounded Agents     │  │  Task System        │             │
│  │  - Scoped workers   │  │  - Task contracts   │             │
│  │  - Time limits       │  │  - Scope definition  │             │
│  │  - Resource limits   │  │  - Progress tracking │             │
│  │  - Result validation │  │  - Verification      │             │
│  └─────────────────────┘  └─────────────────────┘             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Enhanced Ingestion                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Multi-format Ingestion                                     │ │
│  │  - PDF, DOCX, images                                        │ │
│  │  - Web pages, GitHub repositories                           │ │
│  │  - YouTube transcripts                                      │ │
│  │                                                            │ │
│  │  Enhanced Extraction                                        │ │
│  │  - LLM-based concept extraction                            │ │
│  │  - Entity recognition                                       │ │
│  │  - Relationship extraction                                  │ │
│  │  - Importance scoring                                       │ │
│  │                                                            │ │
│  │  Embedding Generation                                       │ │
│  │  - Source embeddings                                         │ │
│  │  - Concept embeddings                                       │ │
│  │  - Memory embeddings                                        │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Conceptual Systems

### 1. Memory System

**Purpose:** Persistent, tiered storage of information with importance signals and retrieval optimization.

**Architecture:**
- **Tiers:** working, conversation, project, knowledge, personal (preserved from current)
- **Importance Scoring:** User-assigned and system-derived importance signals
- **Temporal Weighting:** Recent memories weighted higher in retrieval
- **Curation Interface:** User can edit, promote, demote, or delete memories
- **Retrieval Optimization:** Smart selection based on context, importance, and recency

**Enhancements over Current:**
- User curation capabilities (currently no UI)
- Importance scoring and weighting (currently flat)
- Temporal relevance in retrieval (currently last-N only)
- Memory editing and deletion (currently append-only)

### 2. Source/Provenance System

**Purpose:** Preserve original sources with complete provenance chains and attribution.

**Architecture:**
- **Immutable Sources:** Original content never modified
- **Provenance Chains:** Complete chain from original to derived content
- **Attribution:** All derived content references source IDs
- **Extraction Metadata:** Record methodology and parameters for extractions
- **Distinguishable Types:** Clear labeling of original vs. derived content

**Preserved from Current:**
- Immutable source preservation
- Evidence tracking in graph edges
- Source IDs on all derived content

**Enhancements:**
- Richer provenance metadata
- Extraction methodology recording
- Clear UI distinction between source types
- Provenance visualization

### 3. Knowledge System

**Purpose:** Represent and query knowledge relationships with evidence attribution.

**Architecture:**
- **PostgreSQL-based Graph:** Nodes and edges in relational database
- **Node Types:** concept, entity, person, organization, document, project, conversation
- **Edge Types:** Custom relations with evidence arrays and confidence scores
- **Evidence Attribution:** Every relationship references supporting sources
- **Confidence Scoring:** System and user-assigned confidence levels
- **Temporal Aspects:** Relationship validity over time

**Preserved from Current:**
- Node/edge/evidence model
- Source attribution
- Confidence scoring

**Enhancements:**
- PostgreSQL implementation (currently JSON)
- Richer relationship types
- Temporal validity tracking
- Confidence decay over time
- User-assigned confidence

### 4. Context Assembly Engine

**Purpose:** Assemble optimal context for any request by combining retrieval strategies.

**Architecture:**
- **Enhanced AssembledContext:** Evolution of current pattern
- **Hybrid Retrieval:** Combine keyword, semantic, structured, temporal, and curated signals
- **Dynamic Weighting:** Adjust retrieval strategy based on request type
- **Context Packaging:** Format context optimally for different LLM providers
- **Citation Generation:** Automatic citation assembly from context

**Preserved from Current:**
- AssembledContext pattern
- Source/concept/memory bundling
- Citation generation

**Enhancements:**
- Semantic retrieval (currently keyword only)
- Temporal weighting (currently flat)
- Dynamic weighting (currently static)
- Provider-specific formatting (currently single provider)

### 5. Intent Interpretation

**Purpose:** Understand user intent beyond keyword matching to enable appropriate system behavior.

**Architecture:**
- **LLM-Based Classification:** Use LLM to classify intent (not keyword matching)
- **Ambiguity Detection:** Identify when user intent is unclear
- **Clarification Generation:** Generate appropriate clarification questions
- **Task Decomposition:** Break complex requests into structured tasks
- **Scope Detection:** Identify boundaries of requested work

**Current State:** Keyword-based specialist selection (choose_specialist function)

**Enhancements:**
- LLM-based intent understanding
- Ambiguity detection and clarification
- Task decomposition capabilities
- Scope boundary detection

### 6. Central Orchestrator

**Purpose:** Coordinate all system activity while maintaining user control and system coherence.

**Architecture:**
- **Intent Understanding:** Interpret user requests (see Intent Interpretation system)
- **Context Assembly:** Assemble optimal context (see Context Assembly Engine)
- **Scope Control:** Enforce boundaries and permissions
- **Clarification:** Request user input when intent is ambiguous
- **Execution Coordination:** Coordinate specialists, tools, and agents
- **Verification:** Validate results and request confirmation for consequential actions

**Preserved from Current:**
- Single orchestrator pattern
- Context assembly
- Event streaming

**Enhancements:**
- LLM-based intent understanding (currently keyword-based)
- Scope control and permissions (currently none)
- Clarification flows (currently none)
- Result verification (currently none)
- True multi-specialist coordination (currently single LLM call)

### 7. Model Provider Layer

**Purpose:** Abstract LLM provider details to enable multi-model support and provider flexibility.

**Architecture:**
- **LLMProvider Interface:** Preserved abstract interface
- **Multiple Providers:** Gemini, OpenAI, Anthropic, local models (Ollama)
- **Model Routing:** Select appropriate model based on task type and requirements
- **Fallback Strategy:** Graceful degradation when providers fail
- **Cost Optimization:** Route to cost-effective models when appropriate

**Preserved from Current:**
- LLMProvider abstract interface
- Gemini implementation
- Fallback strategy

**Enhancements:**
- Additional providers (OpenAI, Anthropic, local)
- Model routing logic
- Cost optimization
- Provider-specific context formatting

### 8. Skills System

**Purpose:** Provide reusable knowledge and procedures for task execution.

**Architecture:**
- **Skill Definitions:** Structured representations of how to perform tasks
- **Versioning:** Track skill evolution over time
- **Composition:** Combine skills for complex tasks
- **Application:** Apply skills to specific contexts
- **Validation:** Verify skill application quality

**Current State:** Empty `backend/tools/` directory, documented but not implemented

**Implementation:**
- Skill schema and storage
- Skill definition language
- Skill versioning system
- Skill composition framework
- Skill validation mechanisms

### 9. Tools System

**Purpose:** Provide safe, auditable mechanical capabilities for action execution.

**Architecture:**
- **Tool Registry:** Central registry of available tools
- **Permission System:** Fine-grained permissions for tool invocation
- **Execution Logging:** Complete audit trail of tool usage
- **Safety Bounds:** Resource limits and safety constraints
- **Result Validation:** Verify tool execution results

**Current State:** Empty `backend/tools/` directory, documented but not implemented

**Implementation:**
- Tool schema and interface
- Permission framework
- Execution logging
- Safety constraints
- Result validation

### 10. Bounded Agents/Workers

**Purpose:** Provide reasoning capabilities for scoped tasks without autonomous authority.

**Architecture:**
- **Scoped Workers:** Accept well-defined task boundaries
- **Time Limits:** Maximum execution time per task
- **Resource Limits:** Memory, API call, and operation limits
- **Result Validation:** Structured output with validation criteria
- **Observability:** Complete logging and audit trail

**Current State:** Single orchestrator function, no true agents

**Implementation:**
- Worker schema and interface
- Scope definition framework
- Time and resource limiting
- Result validation
- Observability and logging

**Key Distinction:** Workers are NOT autonomous agents. They operate within strict boundaries defined by the central orchestrator and cannot take independent action.

### 11. Task and Execution System

**Purpose:** Define, track, and verify task execution with clear scope and contracts.

**Architecture:**
- **Task Contracts:** Explicit definition of task scope, boundaries, and success criteria
- **Progress Tracking:** Real-time progress updates and status
- **Verification:** Validate results against success criteria
- **Rollback:** Ability to rollback failed tasks
- **Audit Trail:** Complete record of task execution

**Current State:** No task management system

**Implementation:**
- Task contract schema
- Progress tracking system
- Verification framework
- Rollback mechanisms
- Audit logging

### 12. Permission and Confirmation Model

**Purpose:** Ensure user control over significant system actions.

**Architecture:**
- **Permission System:** Define what actions are allowed under what conditions
- **Scope Boundaries:** Define what systems, files, and data can be affected
- **Confirmation Flows:** Request user confirmation for consequential actions
- **Clarification Flows:** Request user input when intent is ambiguous
- **Verification UI:** Show execution results and request verification

**Current State:** No permission or confirmation system

**Implementation:**
- Permission schema and storage
- Scope boundary definitions
- Confirmation UI components
- Clarification prompt generation
- Verification UI components

## Data Model Evolution

### Enhanced Source Model
- **Current:** id, title, kind, content, created_at, metadata
- **Target:** Add extraction_metadata, embedding_id, importance_score, access_count, last_accessed

### Enhanced Node Model
- **Current:** id, label, type, confidence, source_ids
- **Target:** Add embedding_id, temporal_validity, user_confidence, access_count, created_by

### Enhanced Edge Model
- **Current:** id, source, target, relation, confidence, evidence
- **Target:** Add temporal_validity, user_confidence, strength, created_by, verified_by

### Enhanced Memory Model
- **Current:** id, tier, content, project_id, created_at
- **Target:** Add importance_score, embedding_id, access_count, last_accessed, edited_at, edited_by

### New Models
- **Decision:** id, content, context, alternatives, chosen_alternative, rationale, impact
- **Task:** id, contract, scope, status, progress, result, verification
- **Skill:** id, name, description, procedure, version, dependencies
- **Tool:** id, name, description, permissions, safety_bounds, execution_log
- **Permission:** id, entity, action, scope, conditions, granted_by

## API Evolution

### New Endpoints
- **Intent:** POST /api/intent/interpret, POST /api/intent/clarify
- **Tasks:** POST /api/tasks, GET /api/tasks/{id}, POST /api/tasks/{id}/verify
- **Skills:** GET /api/skills, POST /api/skills, POST /api/skills/{id}/apply
- **Tools:** GET /api/tools, POST /api/tools/{id}/execute
- **Permissions:** GET /api/permissions, POST /api/permissions
- **Decisions:** GET /api/decisions, POST /api/decisions

### Enhanced Endpoints
- **/stream:** Add intent classification, clarification requests, scope validation
- **/memory:** Add importance scoring, editing, deletion
- **/graph:** Add temporal filtering, confidence filtering, user-specific views
- **/search:** Add semantic search, hybrid scoring, temporal weighting

## Security Architecture

### Authentication (Future Multi-User)
- **Current:** None (single-user focus)
- **Target:** Optional authentication for future multi-user support
- **Approach:** Design data models with user_id fields, defer implementation

### Authorization
- **Current:** None
- **Target:** Permission-based authorization
- **Scope:** Tool invocation, data access, task execution

### Audit Logging
- **Current:** None
- **Target:** Complete audit trail of all significant actions
- **Scope:** Tool usage, data modifications, task execution, permission changes

### Data Encryption
- **Current:** None (plain text)
- **Target:** Encryption at rest for sensitive data
- **Scope:** User preferences, API keys, sensitive memories

## Performance Architecture

### Storage Performance
- **Indexing:** Comprehensive database indexing for common query patterns
- **Caching:** Redis or similar for frequently accessed data
- **Connection Pooling:** Database connection pooling for high concurrency
- **Query Optimization:** Query performance monitoring and optimization

### Retrieval Performance
- **Vector Indexing:** pgvector HNSW indexing for fast similarity search
- **Hybrid Scoring:** Efficient hybrid scoring algorithm
- **Result Caching:** Cache common retrieval results
- **Parallel Retrieval:** Parallel execution of retrieval strategies

### API Performance
- **True Token Streaming:** Implement actual token streaming from LLM providers
- **Response Caching:** Cache identical requests
- **Rate Limiting:** Implement rate limiting per user/IP
- **Load Balancing:** Horizontal scaling capability

## Monitoring and Observability

### Metrics
- **System Metrics:** CPU, memory, disk, network
- **Application Metrics:** Request latency, error rates, throughput
- **Business Metrics:** Active users, tasks completed, storage usage

### Logging
- **Structured Logging:** JSON-formatted logs with consistent fields
- **Log Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Aggregation:** Centralized log aggregation and analysis
- **Audit Logging:** Separate audit log for security-relevant events

### Tracing
- **Request Tracing:** Distributed tracing for request flow
- **Error Tracing:** Error context and stack traces
- **Performance Tracing:** Performance bottleneck identification

## Deployment Architecture

### Development
- **Local Development:** Docker Compose with PostgreSQL+pgvector
- **Local LLM:** Optional local model support (Ollama)
- **Mock Services:** Optional mock services for testing

### Production
- **Frontend:** Vercel or similar platform
- **Backend:** Containerized deployment (Kubernetes or similar)
- **Database:** Managed PostgreSQL service (RDS, Cloud SQL, etc.)
- **Monitoring:** Integrated monitoring and alerting
- **Backups:** Automated database backups with point-in-time recovery

### Migration Strategy
- **Zero-Downtime:** Blue-green deployment strategy
- **Data Migration:** Safe migration from JSON to PostgreSQL
- **Rollback:** Ability to rollback to previous version
- **Canary Releases:** Gradual rollout with monitoring

## Non-Goals (Explicitly Out of Scope)

The following are explicitly **NOT** part of the target architecture:

- **LLM Council:** No multi-LLM voting or consensus system
- **Autonomous Multi-Agent Swarm:** No independent autonomous agents
- **Neo4j Integration:** Graph database in PostgreSQL only
- **Enterprise Multi-User SaaS:** Single-user focus with future multi-user possibility
- **Unrestricted Autonomous Execution:** All actions require user control
- **Automatic Storage of Everything:** User-guided capture, not automatic logging

These may be reconsidered in future iterations but are not part of the current target architecture.

## Relationship to Current Architecture

### Preserved Elements
- AssembledContext/context assembly pattern
- Immutable source preservation
- Graph evidence attribution
- Memory tier concept
- SSE streaming architecture
- FastAPI/Next.js separation
- LLM provider abstraction

### Enhanced Elements
- Storage: JSON → PostgreSQL+pgvector
- Retrieval: Keyword-only → Hybrid (keyword + semantic + temporal)
- Intent: Keyword-based → LLM-based classification
- Specialist Selection: Keyword matching → Intent-based routing
- Specialist System: Labels only → True bounded workers
- Frontend: Mocked data → Real backend integration

### New Elements
- Skills system
- Tools system with permissions
- Task contracts and verification
- Permission and confirmation model
- Intent interpretation and clarification
- Enhanced ingestion with multiple formats
- LLM-based concept extraction

## Implementation Phasing

The target architecture will be implemented in phases as described in [ROADMAP.md](ROADMAP.md):

- **Phase 0:** Architecture stabilization and documentation
- **Phase 1:** PostgreSQL migration
- **Phase 2:** Hybrid retrieval implementation
- **Phase 3:** Enhanced context and memory engine
- **Phase 4:** Intent, task contracts, clarification, scope control
- **Phase 5:** Skills and controlled tools
- **Phase 6:** Bounded specialist agents/workers
- **Phase 7:** Dashboard real data integration

Each phase builds on the previous ones, with clear dependencies and definition of done.
