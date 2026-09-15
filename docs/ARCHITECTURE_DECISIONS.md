# Architecture Decisions

> This document records the architectural decisions for Anagrama's evolution into a Personal Intelligence System. Each decision represents a deliberate choice that guides implementation and future development.

## Decision Context

Anagrama is evolving from a functional prototype into a persistent, user-guided Personal Intelligence System. The following decisions establish the technical foundation for this evolution while preserving the strengths of the current implementation.

---

## ADR-001: Primary Storage Strategy

**Status:** Accepted  
**Date:** 2026-09-09  
**Decision:** PostgreSQL will become the primary persistent database.

### Context
The current implementation uses local JSON files for storage (`storage/anagrama-state.json` for graph data, `storage/memory.json` for memory). This works for development but cannot scale for production use.

### Decision
PostgreSQL will become the primary persistent database, eventually storing:
- Projects
- Sources
- Memories
- Decisions
- Tasks
- Skills
- Knowledge nodes
- Relationships
- Provenance metadata

The current JSON storage should be treated as a development/prototype implementation that will eventually be migrated safely.

### Rationale
- PostgreSQL provides ACID guarantees, relational integrity, and proven scalability
- Enables complex queries across entities (projects, sources, memories, relationships)
- pgvector extension provides vector similarity search capabilities
- Mature ecosystem, tooling, and operational expertise
- Supports future multi-user scenarios if needed

### Consequences
- Migration strategy must ensure no data loss during transition
- Database schema design must support existing data models
- Performance considerations for graph queries in relational database
- Requires connection pooling, migration tooling, and backup strategy

### Migration Timing
**Phase 1** of the implementation roadmap. Do not implement migration yet.

---

## ADR-002: Semantic Retrieval Approach

**Status:** Accepted  
**Date:** 2026-09-09  
**Decision:** pgvector will be used for semantic/vector retrieval with hybrid approach.

### Context
Current retrieval is keyword-only substring matching. This limits the system's ability to find semantically related content and understand context.

### Decision
Retrieval should eventually be hybrid, combining:
- Keyword/full-text search (PostgreSQL native)
- Semantic/vector similarity (pgvector)
- Structured project context filtering
- Temporal relevance scoring
- Explicitly curated memories weighting

### Rationale
- Hybrid approach balances precision (keywords) with semantic understanding (vectors)
- Keyword search remains important for exact matches and proper nouns
- Vector search enables finding related concepts beyond exact term matches
- Temporal and contextual filtering ensures relevance to current work
- User curation allows explicit importance signals

### Consequences
- Requires embedding generation for all sources and knowledge nodes
- Embedding storage and indexing strategy needed
- Hybrid scoring algorithm development required
- Trade-off between computational cost and retrieval quality

### Implementation Timing
**Phase 2** of the implementation roadmap. Do not implement embeddings yet.

---

## ADR-003: Knowledge Graph Storage

**Status:** Accepted  
**Date:** 2026-09-09  
**Decision:** Knowledge relationships will initially be represented within PostgreSQL.

### Context
The Docker Compose file includes Neo4j, but no Neo4j integration exists. Some documentation suggests Neo4j for graph storage.

### Decision
Do not introduce Neo4j in the immediate implementation phase. Knowledge relationships should initially be represented within PostgreSQL using:
- Nodes table (knowledge nodes, entities, concepts)
- Edges table (relationships between nodes)
- Evidence attribution (source IDs supporting relationships)
- Confidence scoring for relationships

Neo4j may be reconsidered later if PostgreSQL-based graph querying becomes insufficient.

### Rationale
- Reduces infrastructure complexity and operational overhead
- PostgreSQL is already chosen as primary storage (ADR-001)
- Modern PostgreSQL handles graph queries adequately for current scale
- Avoids premature optimization; defer graph database until proven necessary
- Single database simplifies backup, migration, and transaction management

### Consequences
- Graph query performance must be monitored as data grows
- Relationship traversal may be less efficient than native graph databases
- Schema design must optimize for common graph query patterns
- Migration path to Neo4j remains possible if needed

### Reconsideration Criteria
Consider Neo4j if:
- Graph queries exceed acceptable performance thresholds
- Relationship complexity grows beyond relational optimization
- Multi-hop traversals become performance bottlenecks

---

## ADR-004: Central Orchestrator Pattern

**Status:** Accepted  
**Date:** 2026-09-09  
**Decision:** Anagrama should use one central orchestrator, not autonomous multi-agent swarm.

### Context
Current implementation has a single orchestrator function. Some documentation described a multi-agent system with OpenAI Agents SDK, but this was removed.

### Decision
Anagrama should use one central orchestrator. Specialists or workers may eventually be invoked for bounded tasks, but they should not operate as independent autonomous authorities.

The central system should remain responsible for:
- Understanding user intent
- Assembling appropriate context
- Scope control and boundary enforcement
- Clarification when intent is ambiguous
- Permission enforcement
- Execution coordination
- Result verification

### Rationale
- Central orchestrator maintains overall system coherence and user control
- Prevents autonomous agents from taking actions outside user intent
- Enables consistent permission enforcement and scope control
- Simplifies debugging and observability
- Reduces risk of unintended agent interactions
- Aligns with "user-guided" system philosophy

### Consequences
- Specialist/workers must be designed as bounded, scoped tasks
- Central orchestrator requires comprehensive context assembly
- Need clear protocols for specialist invocation and result handling
- Performance considerations for centralized coordination

### Specialist/Worker Design
Specialists/workers should:
- Accept well-defined inputs with clear scope boundaries
- Return structured outputs with provenance
- Not autonomously invoke other specialists without central coordination
- Operate within time and resource limits
- Be observable and auditable

---

## ADR-005: Tools, Skills, and Agents Separation

**Status:** Accepted  
**Date:** 2026-09-09  
**Decision:** Tools, Skills, and Agents must remain separate concepts with clear boundaries.

### Context
The current `backend/tools/` directory is empty. Documentation exists but implementation is missing. These concepts need clear definition.

### Decision

**TOOLS** are mechanical capabilities that perform actions:
- File operations (read, write, upload)
- API calls (external services, GitHub, web scraping)
- Database operations (queries, updates)
- System operations (execute commands, run processes)

**SKILLS** are structured knowledge/instructions describing how tasks should be performed:
- Task decomposition patterns
- Step-by-step procedures
- Best practices and guidelines
- Quality criteria and validation rules
- Domain-specific knowledge

**AGENTS** are reasoning workers that may use skills and tools for bounded tasks:
- Accept scoped task definitions
- Apply relevant skills
- Invoke appropriate tools
- Return structured results
- Operate within defined boundaries

### Rationale
- Clear separation enables independent evolution of each layer
- Tools can be reused across different skills and agents
- Skills provide reusable knowledge without requiring reasoning
- Agents provide flexible reasoning within controlled boundaries
- Separation supports testing, composition, and maintainability

### Consequences
- Tool system must be designed for safe, auditable execution
- Skill system requires structured representation and versioning
- Agent system needs clear scope definition and sandboxing
- Integration points between layers must be well-defined

### Implementation Timing
**Phase 5** (Skills and Tools) and **Phase 6** (Bounded Agents). Do not implement these systems yet.

---

## ADR-006: Single-User First Architecture

**Status:** Accepted  
**Date:** 2026-09-09  
**Decision:** Immediate architecture optimized for single primary user with future multi-user support possible.

### Context
Current implementation has no authentication or user management. The target is a Personal Intelligence System, primarily for individual use.

### Decision
The immediate architecture is optimized for a single primary user. However, major persistent entities should eventually be designed so future multi-user support remains possible.

### Rationale
- Personal Intelligence System is primarily individual-focused
- Single-user architecture simplifies initial implementation
- Avoids premature complexity of authentication, authorization, multi-tenancy
- Allows focus on core intelligence capabilities first
- Design for future multi-user without building it now

### Design Principles for Future Multi-User Support
- Entity ownership should be trackable (user_id fields)
- Access control should be designable (permission fields)
- Data isolation should be possible (per-user filtering)
- Sharing/collaboration should be architecturally possible

### Consequences
- No enterprise authentication system initially
- No complex permission system initially
- User management can be simple (single configured user)
- Data models should include user_id fields even if not used immediately

### Implementation Timing
Single-user focus for **Phases 0-6**. Multi-user considerations in entity design throughout.

---

## ADR-007: Source Preservation and Provenance

**Status:** Accepted  
**Date:** 2026-09-09  
**Decision:** Original sources must remain distinguishable from derived content.

### Context
The current implementation preserves full source content with evidence tracking. This principle must be maintained and strengthened.

### Decision
Original sources must remain distinguishable from:
- AI-generated summaries
- Extracted concepts
- Derived memories
- Interpretations
- Decisions

The architecture should preserve provenance and relationships back to original material whenever possible.

### Rationale
- Users must be able to distinguish original from derived content
- Provenance enables verification and fact-checking
- Attributable information supports trust and accountability
- Original sources may need to be re-interpreted as understanding evolves
- Prevents important information from being silently lost in AI processing

### Implementation Requirements
- Sources are immutable once created
- All derived content must reference source IDs
- Extraction processes must record methodology and parameters
- Summaries and interpretations must be clearly labeled as such
- Chain of custody from original to derived must be traceable

### Consequences
- Storage requirements higher (preserve full originals)
- Schema design must support provenance chains
- UI must clearly distinguish source types
- Deletion policies must consider derived dependencies

---

## ADR-008: User Control and Scope Boundaries

**Status:** Accepted  
**Date:** 2026-09-09  
**Decision:** Future significant actions should support explicit permissions, scope boundaries, and confirmation.

### Context
Current implementation has no permission system or confirmation flows. Actions execute without user oversight.

### Decision
Future significant actions should support:
- Explicit permissions (what can be done)
- Scope boundaries (what is affected)
- Clarification when intent is materially ambiguous
- Confirmation for consequential actions
- Verification of execution results

### Rationale
- User control is fundamental to "user-guided" system philosophy
- Prevents unintended consequences from ambiguous instructions
- Enables trust through transparency and confirmation
- Supports accountability and auditability
- Aligns with human-in-the-loop principles

### Implementation Requirements
- Permission system for tool/agent invocation
- Scope definition for tasks (what files, what systems, what data)
- Ambiguity detection and clarification prompts
- Confirmation UI for destructive or high-impact actions
- Result verification and reporting

### Consequences
- More user interaction overhead (trade-off for safety)
- Requires UI for permissions, confirmations, verification
- System complexity increases with permission model
- Performance considerations for verification steps

### Implementation Timing
**Phase 4** (Intent, task contracts, clarification, scope control).

---

## ADR-009: Preserve Existing Architectural Foundations

**Status:** Accepted  
**Date:** 2026-09-09  
**Decision:** Preserve and evolve existing architectural patterns rather than unnecessary rebuilding.

### Context
The current implementation has several solid architectural patterns that should be preserved.

### Decision
The following existing architecture should be preserved and evolved rather than unnecessarily rebuilt:
- AssembledContext/context assembly pattern
- Immutable source preservation
- Graph evidence attribution
- Memory tier concept
- SSE streaming architecture
- FastAPI/Next.js separation
- LLM provider abstraction

### Rationale
- These patterns are well-designed and functional
- Preserving them reduces implementation risk
- Evolution is faster than rebuilding
- Maintains continuity with existing codebase
- Leverages existing investment and testing

### Evolution Strategy
- Enhance context assembly with more sophisticated retrieval
- Extend source preservation with better provenance tracking
- Improve graph attribution with confidence scoring
- Expand memory tiers with curation and importance signals
- Enhance streaming with true token streaming
- Add more LLM providers to existing abstraction
- Maintain separation but improve integration patterns

### Consequences
- Some legacy patterns may constrain future optimizations
- Evolution must maintain backward compatibility where possible
- Technical debt may accumulate in evolved patterns
- Need to balance preservation with necessary refactoring

---

## Non-Goals (Explicitly Out of Scope)

The following are explicitly **NOT** being built in the current architecture:

- **LLM Council**: No multi-LLM voting or consensus system
- **Autonomous Multi-Agent Swarm**: No independent autonomous agents
- **Neo4j Integration**: Graph database in PostgreSQL only (ADR-003)
- **Enterprise Multi-User SaaS**: Single-user focus initially (ADR-006)
- **Unrestricted Autonomous Execution**: All actions require user control (ADR-008)
- **Automatic Storage of Everything**: User-guided capture, not automatic logging

These may be reconsidered in future iterations but are not part of the current architectural direction.

---

## Decision Record Maintenance

This document should be updated when:
- New architectural decisions are made
- Existing decisions are reconsidered or reversed
- Implementation reveals consequences not anticipated
- Context changes significantly enough to affect decisions

Each decision should reference its ADR number for traceability.
