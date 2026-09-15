# Architecture Documentation Summary

> This document provides a summary of the architecture documentation created for Anagrama's evolution into a Personal Intelligence System.

## Created Documentation

### 1. ARCHITECTURE_DECISIONS.md
**Purpose:** Records architectural decisions with rationale, consequences, and reconsideration criteria.

**Key Decisions Documented:**
- ADR-001: Primary Storage Strategy (PostgreSQL)
- ADR-002: Semantic Retrieval Approach (pgvector + hybrid)
- ADR-003: Knowledge Graph Storage (PostgreSQL-based, not Neo4j)
- ADR-004: Central Orchestrator Pattern (single orchestrator, not autonomous swarm)
- ADR-005: Tools, Skills, and Agents Separation (clear conceptual boundaries)
- ADR-006: Single-User First Architecture (with future multi-user possibility)
- ADR-007: Source Preservation and Provenance (immutable sources, distinguishable derived content)
- ADR-008: User Control and Scope Boundaries (permissions, confirmation, verification)
- ADR-009: Preserve Existing Architectural Foundations (evolution, not rebuilding)

**Non-Goals Explicitly Documented:**
- LLM Council
- Autonomous multi-agent swarm
- Neo4j integration
- Enterprise multi-user SaaS
- Unrestricted autonomous execution
- Automatic storage of everything

### 2. CURRENT_ARCHITECTURE.md
**Purpose:** Comprehensive documentation of the current implementation state.

**Sections:**
- Technology stack (Frontend, Backend, Storage, Infrastructure)
- Architecture diagram with current data flow
- Component detail (Frontend, Backend, Storage, Retrieval, LLM, Ingestion)
- Current limitations (Storage, Retrieval, Orchestration, Frontend, Ingestion)
- Technical debt (Documentation, Code Quality, Infrastructure)
- Security considerations
- Performance characteristics
- Known issues (Critical, High, Medium, Low priority)
- Testing status
- Deployment status
- Summary of strengths and gaps

**Key Finding:** Functional prototype with excellent architectural patterns but significant implementation gaps before production readiness.

### 3. TARGET_ARCHITECTURE.md
**Purpose:** Description of the planned target architecture for Personal Intelligence System.

**Vision Statement:** Persistent, user-guided system that preserves knowledge, conversations, ideas, projects, decisions, sources, goals, context, and preferences.

**Sections:**
- High-level architecture diagram
- 12 conceptual systems (Memory, Source/Provenance, Knowledge, Context Assembly, Intent Interpretation, Central Orchestrator, Model Provider, Skills, Tools, Bounded Agents, Task System, Permission/Confirmation)
- Data model evolution
- API evolution
- Security architecture
- Performance architecture
- Monitoring and observability
- Deployment architecture
- Relationship to current architecture
- Implementation phasing overview

**Key Principle:** Important information should be persistently preserved, attributable, addressable, and retrievable independently of any individual LLM context window.

### 4. CONCEPTS.md
**Purpose:** Defines key conceptual systems and boundaries with shared vocabulary.

**Core Philosophy:** User-guided Personal Intelligence System with principles of user control, persistent preservation, provenance, clarity, and continuity.

**Conceptual Systems Documented:**
1. Memory System (tiered storage with importance and temporal weighting)
2. Source/Provenance System (immutable sources with provenance chains)
3. Knowledge System (graph-based relationships with evidence attribution)
4. Context Assembly Engine (hybrid retrieval with dynamic weighting)
5. Intent Interpretation (LLM-based classification with ambiguity detection)
6. Central Orchestrator (coordination with user control)
7. Model Provider Layer (abstraction for multi-model support)
8. Skills System (structured knowledge representation)
9. Tools System (safe, auditable mechanical capabilities)
10. Bounded Agents/Workers (reasoning within strict boundaries)
11. Task and Execution System (contracts, tracking, verification)
12. Permission and Confirmation Model (user control over actions)

**Key Distinctions:**
- Tools vs. Skills vs. Agents (mechanical vs. knowledge vs. reasoning)
- Intent vs. Task vs. Execution (understanding vs. planning vs. action)
- Permission vs. Scope vs. Confirmation (authorization vs. boundaries vs. approval)
- Source vs. Memory vs. Knowledge (raw material vs. refined insights vs. connected understanding)

### 5. ROADMAP.md
**Purpose:** Phased implementation plan with clear dependencies and definition of done.

**7 Phases:**
- **Phase 0:** Architecture stabilization and documentation (1-2 weeks)
- **Phase 1:** Persistent data foundation - PostgreSQL migration (4-6 weeks)
- **Phase 2:** Hybrid retrieval - keyword + semantic + temporal (4-6 weeks)
- **Phase 3:** Real context and memory engine (4-6 weeks)
- **Phase 4:** Intent, task contracts, clarification, scope control (6-8 weeks)
- **Phase 5:** Skills and controlled tools (6-8 weeks)
- **Phase 6:** Bounded specialist agents/workers (6-8 weeks)
- **Phase 7:** Dashboard real data integration (4-6 weeks)

**Each Phase Includes:**
- Purpose and dependencies
- Major implementation work
- Risks and mitigation
- Definition of done with checkboxes

**Cross-Cutting Concerns:**
- Testing strategy
- Documentation strategy
- Monitoring and observability
- Security considerations

**Success Metrics:** Quantitative metrics for each phase.

### 6. Updated Documentation
- **AGENT_ARCHITECTURE.md:** Marked as deprecated with reference to current architecture
- **README.md:** Updated to reflect current Gemini implementation and new documentation structure

## Architecture Decisions Summary

### Storage Strategy
- **Decision:** PostgreSQL as primary database with pgvector for semantic search
- **Rationale:** ACID guarantees, relational integrity, proven scalability, mature ecosystem
- **Current:** JSON files (development adapters)
- **Timeline:** Phase 1 implementation

### Retrieval Strategy
- **Decision:** Hybrid retrieval (keyword + semantic + structured + temporal + curated)
- **Rationale:** Balances precision with semantic understanding, enables relevance ranking
- **Current:** Keyword-only substring matching
- **Timeline:** Phase 2 implementation

### Knowledge Graph Strategy
- **Decision:** PostgreSQL-based graph (not Neo4j initially)
- **Rationale:** Reduces complexity, PostgreSQL already chosen, adequate for current scale
- **Current:** JSON-based graph
- **Timeline:** Phase 1 implementation (with PostgreSQL)
- **Reconsideration:** If PostgreSQL graph queries become insufficient

### Orchestration Strategy
- **Decision:** Single central orchestrator (not autonomous multi-agent swarm)
- **Rationale:** Maintains user control, ensures coherence, simplifies debugging
- **Current:** Single orchestrator function
- **Timeline:** Enhanced in Phases 4-6

### Conceptual Boundaries
- **Decision:** Clear separation between Tools (mechanical), Skills (knowledge), Agents (reasoning)
- **Rationale:** Independent evolution, reusability, testing, composition
- **Current:** Empty tools directory, documented but not implemented
- **Timeline:** Phases 5-6 implementation

### User Strategy
- **Decision:** Single-user first with future multi-user possibility
- **Rationale:** Focus on core capabilities, avoid premature complexity
- **Current:** No authentication
- **Timeline:** Single-user focus through Phase 6, multi-user considerations in design

### Preservation Strategy
- **Decision:** Immutable sources with provenance chains, distinguishable from derived content
- **Rationale:** Verification, fact-checking, re-interpretation, prevents information loss
- **Current:** Immutable sources with evidence tracking (good foundation)
- **Timeline:** Enhanced throughout Phases 1-3

### Control Strategy
- **Decision:** Explicit permissions, scope boundaries, clarification, confirmation, verification
- **Rationale:** User control, prevents unintended consequences, transparency
- **Current:** No permission or confirmation system
- **Timeline:** Phase 4 implementation

### Evolution Strategy
- **Decision:** Preserve existing patterns (AssembledContext, source preservation, SSE streaming, etc.)
- **Rationale:** Reduces risk, leverages investment, maintains continuity
- **Current:** Solid patterns identified
- **Timeline:** Continuous enhancement throughout all phases

## Contradictions Between Current Code and Target Architecture

### 1. Documentation vs. Implementation
- **Issue:** Multiple docs describe removed OpenAI/Agents-SDK system
- **Evidence:** `backend/agents/__pycache__/definitions.cpython-312.pyc` proves removed code
- **Resolution:** AGENT_ARCHITECTURE.md marked as deprecated, docs updated to reflect current Gemini implementation

### 2. Infrastructure vs. Implementation
- **Issue:** Docker Compose provisions PostgreSQL and Neo4j, but code doesn't use them
- **Current:** JSON storage only
- **Target:** PostgreSQL with pgvector, Neo4j deferred
- **Resolution:** Architecture decision to use PostgreSQL-only initially, Neo4j reconsidered if needed

### 3. Dashboard vs. Backend
- **Issue:** Dashboard UI is 90% mocked, backend has real data
- **Current:** Chat input only wired to backend
- **Target:** Full dashboard integration with real data
- **Resolution:** Phase 7 dedicated to dashboard real data integration

### 4. Specialist System
- **Issue:** Documentation describes multi-agent system, code has single orchestrator
- **Current:** Keyword-based specialist selection, single LLM call
- **Target:** LLM-based intent classification, bounded workers
- **Resolution:** Enhanced specialist system in Phases 4-6

### 5. Dead Code
- **Issue:** Root `app/` + `src/` frontend exists but is unreachable
- **Current:** Dead code cluttering repository
- **Target:** Clean repository with single frontend
- **Resolution:** Not addressed in current roadmap (could be cleanup task)

## Next Implementation Task

**Exact Next Task:** Begin Phase 1 - PostgreSQL Migration

**Specific First Steps:**
1. Design PostgreSQL schema for all entities (sources, nodes, edges, memories, projects, etc.)
2. Design indexing strategy for common query patterns
3. Design migration schema from JSON structure
4. Create migration scripts with rollback capability
5. Implement PostgreSQL adapter for graph storage
6. Implement PostgreSQL adapter for memory storage
7. Maintain existing interface (graph.add_source(), memory.add(), etc.)

**Prerequisites:**
- Phase 0 must be complete (architecture stabilization and documentation)
- PostgreSQL instance available (local or cloud)
- Migration strategy reviewed and approved
- Backup procedures established

**Success Criteria:**
- Zero data loss in migration testing
- All existing tests pass with new storage adapters
- Performance meets or exceeds current JSON performance
- Rollback procedures tested and documented

**DO NOT BEGIN AUTOMATICALLY:** This task should not be started without explicit user approval and confirmation that Phase 0 is complete and the architectural direction is approved.

## Files Created or Modified

### Created Files
1. `docs/ARCHITECTURE_DECISIONS.md` - Architectural decision records
2. `docs/CURRENT_ARCHITECTURE.md` - Current implementation state
3. `docs/TARGET_ARCHITECTURE.md` - Planned target architecture
4. `docs/CONCEPTS.md` - Conceptual systems and boundaries
5. `docs/ROADMAP.md` - Phased implementation plan
6. `docs/ARCHITECTURE_SUMMARY.md` - This summary document

### Modified Files
1. `docs/AGENT_ARCHITECTURE.md` - Marked as deprecated with references to current docs
2. `README.md` - Updated to reflect current implementation and new documentation structure

## Summary

The architecture documentation establishes a clear technical direction for Anagrama's evolution from a functional prototype to a Personal Intelligence System. The documentation:

1. **Preserves Strengths:** Identifies and commits to preserving excellent existing patterns (AssembledContext, source preservation, SSE streaming, etc.)

2. **Addresses Gaps:** Provides clear solutions for critical gaps (storage, retrieval, intent understanding, user control)

3. **Establishes Boundaries:** Defines clear conceptual boundaries (Tools vs. Skills vs. Agents, Intent vs. Task vs. Execution)

4. **Provides Roadmap:** Offers a phased implementation plan with clear dependencies and success criteria

5. **Maintains Control:** Emphasizes user control throughout (permissions, confirmation, verification, scope boundaries)

6. **Enables Evolution:** Designs for future multi-user support and extensibility while focusing on single-user first

The architecture is ready for implementation to begin with Phase 1 (PostgreSQL Migration) upon user approval.
