# Persistence Design Summary

> This document summarizes the PostgreSQL persistence architecture design for Anagrama, including schema proposal, migration strategy, and key decisions.

## Files Created

1. **docs/PERSISTENCE_ARCHITECTURE.md** (12715 bytes)
   - Core data principle (canonical vs. derived vs. relationships)
   - Data classification framework
   - Provenance model with three implementation strategies
   - Mutability strategy (immutable, versioned, mutable, soft delete)
   - Retention and deletion policy
   - Performance considerations
   - Schema evolution strategy
   - Security considerations
   - Open questions and trade-offs

2. **docs/DATABASE_SCHEMA_PROPOSAL.md** (48163 bytes)
   - Entity relationship diagram (Mermaid)
   - 25 table definitions with detailed specifications
   - Canonical vs. derived data classification for each table
   - Primary key strategy (UUID for all tables)
   - Foreign key relationships
   - Mutability expectations
   - Retention considerations
   - Comprehensive indexing strategy
   - Key design decisions with rationale
   - Schema summary (15 canonical, 5 derived, 4 relationship, 1 provenance)

3. **docs/MIGRATION_STRATEGY.md** (38608 bytes)
   - Current JSON storage analysis
   - Migration goals (zero data loss, rollback capability)
   - 6-phase migration approach
   - Detailed migration steps with Python code examples
   - ID preservation strategy (UUID v5 conversion)
   - Relationship migration strategy
   - Post-migration validation (5 validation steps)
   - Rollback strategy and triggers
   - Complete migration script template
   - Timeline estimates by dataset size
   - Risks and mitigation strategies
   - Success criteria checklist

## Proposed Schema Summary

### Table Count: 25 Tables

#### Canonical Data Tables (15)
- users, projects, sources, source_files, memories, memory_versions, decisions, tasks, task_state_history, user_preferences, knowledge_nodes, knowledge_edges, skills, skill_versions

#### Derived Data Tables (5)
- embeddings, summaries, extracted_entities, extracted_concepts, classifications_auto

#### Relationship Tables (4)
- source_memory_links, memory_project_links, decision_evidence_links, edge_evidence_links

#### Provenance Tables (1)
- provenance_records

### Key Schema Characteristics

#### Primary Keys
- **Strategy:** UUID for all tables
- **Rationale:** Distributed compatibility, no exposed internal IDs, easier merging
- **Implementation:** PostgreSQL `gen_random_uuid()` default

#### Foreign Keys
- **Strategy:** Enforced FKs for canonical data, logical references for derived data
- **Rationale:** Referential integrity for canonical data, flexibility for derived data
- **Implementation:** Explicit FK constraints for core tables, logical references for derived

#### Soft Deletes
- **Strategy:** `deleted_at` timestamp for most tables
- **Rationale:** Recovery capability, audit trail, cascade safety
- **Implementation:** WHERE deleted_at IS NULL for active record queries

#### JSONB Usage
- **Strategy:** JSONB for flexible metadata and procedure storage
- **Rationale:** Schema evolution without migrations, flexible data structures
- **Implementation:** GIN indexes for JSONB queries

#### Timestamp Strategy
- **Strategy:** TIMESTAMP WITHOUT TIME ZONE
- **Rationale:** Simpler handling, consistent with current JSON timestamps
- **Implementation:** NOW() defaults, explicit timezone handling in application

## Canonical vs. Derived Data Model

### Canonical Data Characteristics
- **Immutable or Versioned:** Original content never silently overwritten
- **User-Controlled:** User can modify (with versioning)
- **High Retention:** Permanent or long-term retention
- **Strong Provenance:** Complete attribution tracking
- **Examples:** sources, memories, decisions, projects, tasks

### Derived Data Characteristics
- **Regenerable:** Can be recreated from canonical data
- **System-Generated:** Created by AI or algorithms
- **Lower Retention:** Can be regenerated (shorter retention acceptable)
- **Origin References:** Must reference canonical sources
- **Examples:** embeddings, summaries, extracted entities, classifications

### Relationship Data Characteristics
- **Attribution:** Connects entities to their origins
- **Evidence:** Links decisions/memories to supporting sources
- **Provenance:** Tracks derivation chains
- **Immutable:** Once created, never modified
- **Examples:** source_memory_links, decision_evidence_links, provenance_records

## Provenance Model

### Provenance Requirements
Every derived record must preserve:
- **Origin Reference:** ID of canonical source(s)
- **Creation Timestamp:** When was this derived?
- **Generation Method:** How was this derived?
- **Model/Provider:** Which AI model or algorithm?
- **Parameters:** What parameters were used?
- **Confidence:** How confident is the system?
- **Version:** Version of generation method/model
- **Chain of Custody:** Complete derivation chain

### Implementation Strategy
**Hybrid Approach:**
- **Embedded Provenance:** For simple derivations (embeddings, summaries)
- **Separate Provenance Table:** For complex derivation chains
- **Centralized Tracking:** `provenance_records` table for comprehensive tracking

### Provenance Table Structure
```sql
CREATE TABLE provenance_records (
    id UUID PRIMARY KEY,
    derived_record_id UUID NOT NULL,
    derived_record_type VARCHAR(50) NOT NULL,
    origin_record_id UUID NOT NULL,
    origin_record_type VARCHAR(50) NOT NULL,
    generation_method VARCHAR(100) NOT NULL,
    model_used VARCHAR(100),
    model_version VARCHAR(50),
    parameters JSONB DEFAULT '{}',
    generated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    confidence FLOAT,
    chain_of_custody UUID[] DEFAULT ARRAY[]::UUID[]
);
```

## Indexing Strategy

### Primary Indexes
- All tables: PRIMARY KEY on `id` (UUID)

### Foreign Key Indexes
- All foreign keys: INDEX for JOIN performance

### Query Pattern Indexes
- `project_id` - Project-scoped queries (very common)
- `user_id` - User-scoped queries (common)
- `created_at` - Temporal queries (common)
- `deleted_at` - Filtering active records (very common)
- `type` fields - Type filtering (common)

### Specialized Indexes
- **HNSW Index:** `embeddings.vector` for semantic search (pgvector)
- **GIN Indexes:** JSONB fields for flexible queries
- **GIN Index:** `provenance_records.chain_of_custody` for chain traversal
- **Composite Indexes:** Multi-column query optimization

### Future Indexes
- Full-text search indexes (PostgreSQL tsvector)
- BRIN indexes for time-series data
- Partial indexes for filtered queries
- Covering indexes for specific query patterns

## Migration Strategy Summary

### Current JSON Storage
- **storage/anagrama-state.json:** nodes, edges, sources, projects
- **storage/memory.json:** memory entries with tiers
- **ID Format:** `prefix_randomstring` (e.g., `node_abc123`)
- **Relationships:** Arrays (source_ids, evidence)

### Migration Approach
**6-Phase Strategy:**
1. **Preparation and Validation:** Backup, analysis, connectivity validation
2. **Schema Setup:** Create tables, indexes, extensions
3. **Data Migration:** Transform and load JSON data with ID conversion
4. **Relationship Migration:** Preserve all relationships
5. **Post-Migration Validation:** Counts, integrity, checksums, queries
6. **Adapter Switch:** Future PostgreSQL adapter implementation

### ID Preservation Strategy
**UUID v5 Conversion:**
- **Approach:** UUID v5 (namespace-based) from JSON string IDs
- **Namespace:** Fixed UUID for Anagrama
- **Benefits:** Deterministic, traceable, no collisions
- **Implementation:** `uuid.uuid5(namespace, json_id_string)`

### Migration Safety
**Zero Data Loss Guarantees:**
- Pre-migration backup with checksums
- Read-only JSON processing
- Transactional inserts
- Record count validation
- Referential integrity validation
- Rollback capability

### Rollback Strategy
**Triggers:** Validation failures, count mismatches, integrity violations
**Procedure:** Drop database, restore JSON files, restart application
**Validation:** Checksum validation, application functionality test

## Highest-Risk Migration Areas

### 1. ID Conversion (HIGH RISK)
**Risk:** UUID v5 conversion might produce collisions if JSON IDs are not unique
**Mitigation:** Validate JSON ID uniqueness before migration, use namespace-based UUIDs
**Validation:** Post-migration ID uniqueness check

### 2. Relationship Preservation (HIGH RISK)
**Risk:** Complex array-based relationships in JSON might not be preserved correctly
**Mitigation:** Explicit relationship migration, referential integrity validation
**Validation:** Compare relationship counts pre/post migration

### 3. Data Loss During Migration (MEDIUM RISK)
**Risk:** Records might be lost if migration script fails mid-process
**Mitigation:** Transactional inserts, comprehensive backup, rollback capability
**Validation:** Record count comparison, checksum validation

### 4. Schema Mismatch (MEDIUM RISK)
**Risk:** PostgreSQL schema might not accommodate all JSON data structures
**Mitigation:** Comprehensive JSON analysis, flexible JSONB fields, schema validation
**Validation:** Data integrity validation, sample query testing

### 5. Performance Issues (LOW-MEDIUM RISK)
**Risk:** Migration might be slow for large datasets
**Mitigation:** Batch inserts, progress monitoring, performance testing
**Validation:** Performance benchmarks, timeline estimation

## Schema Decisions Requiring Human Approval

### 1. UUID Primary Keys (DECISION REQUIRED)
**Question:** Should we use UUIDs for all primary keys, or use integers for some tables?
**Trade-off:** UUIDs are larger and slower but provide better distributed compatibility
**Recommendation:** UUIDs for all tables (as proposed)
**Alternative:** Integers for high-volume tables (embeddings, extracted_entities)

### 2. Soft Delete Strategy (DECISION REQUIRED)
**Question:** Should we use soft deletes (`deleted_at`) for all tables, or hard delete some?
**Trade-off:** Soft deletes enable recovery but increase storage and query complexity
**Recommendation:** Soft deletes for most tables, hard delete for temporary/derived data
**Alternative:** Hard delete for all tables with separate audit log

### 3. ID Conversion Strategy (DECISION REQUIRED)
**Question:** Should we use UUID v5 conversion, or store original JSON IDs as strings?
**Trade-off:** UUID v5 is deterministic but loses original ID format
**Recommendation:** UUID v5 conversion (as proposed)
**Alternative:** Store original JSON IDs in separate column, use new UUIDs

### 4. JSONB vs. Normalized Metadata (DECISION REQUIRED)
**Question:** Should we use JSONB for metadata, or normalize into separate tables?
**Trade-off:** JSONB is flexible but less performant for complex queries
**Recommendation:** JSONB for metadata (as proposed)
**Alternative:** Normalize critical metadata into separate tables

### 5. Provenance Storage Strategy (DECISION REQUIRED)
**Question:** Should we use embedded provenance, separate table, or hybrid approach?
**Trade-off:** Embedded is simpler, separate is more powerful, hybrid balances both
**Recommendation:** Hybrid approach (as proposed)
**Alternative:** Centralized provenance table for all derivations

### 6. Project Assignment for Migrated Data (DECISION REQUIRED)
**Question:** How should we assign sources to projects if not explicitly linked in JSON?
**Trade-off:** Auto-assign based on heuristics vs. manual assignment vs. default project
**Recommendation:** Manual review and assignment (most safe)
**Alternative:** Auto-assign based on content similarity or create default project

### 7. Default User for Migrated Data (DECISION REQUIRED)
**Question:** How should we handle the default user for migrated data?
**Trade-off:** Create special "migrated" user vs. assign to first real user vs. nullable user_id
**Recommendation:** Create special "system" user for migrated data
**Alternative:** Make user_id nullable initially, require user to claim data

## Key Architectural Decisions

### 1. Canonical vs. Derived Separation
**Decision:** Explicit separation of canonical and derived data with different retention policies
**Rationale:** Prevents silent overwriting of original data, enables safe regeneration
**Impact:** Requires careful data classification and provenance tracking

### 2. Provenance Tracking
**Decision:** Comprehensive provenance tracking for all derived data
**Rationale:** Attribution, verification, audit trails, reproducibility
**Impact:** Additional storage and query complexity

### 3. Soft Delete Pattern
**Decision:** Soft deletes for most entities with cascade to derived data
**Rationale:** Recovery capability, audit trail, safe cascade operations
**Impact:** Additional storage, query complexity (WHERE deleted_at IS NULL)

### 4. UUID Primary Keys
**Decision:** UUIDs for all primary keys with deterministic conversion from JSON IDs
**Rationale:** Distributed compatibility, no exposed internal IDs, traceability
**Impact:** Larger storage, slightly slower than integers

### 5. JSONB for Flexibility
**Decision:** JSONB for metadata and flexible data structures
**Rationale:** Schema evolution without migrations, flexibility
**Impact:** Less schema validation, slower complex queries

### 6. Relationship Tables
**Decision:** Explicit relationship tables instead of JSONB arrays
**Rationale:** Query performance, referential integrity, easier indexing
**Impact:** More tables, more joins

### 7. Version History
**Decision:** Separate version tables for user-editable entities
**Rationale:** Audit trail, rollback capability, query performance
**Impact:** Additional storage, more complex queries

## Open Questions

1. **ID Conversion:** Is UUID v5 the right approach, or should we preserve original string IDs?
2. **Default User:** How should we handle the default user for migrated data?
3. **Project Assignment:** How should we assign unlinked sources to projects?
4. **Timestamp Precision:** How should we handle timestamp precision differences?
5. **Large Content:** How should we handle very large source content?
6. **Concurrent Access:** How should we handle concurrent access during migration?
7. **Performance Targets:** What are the specific performance targets for queries?
8. **Retention Policies:** What are the specific retention periods for derived data?

## Risks and Trade-offs

### Normalization vs. JSONB
- **Decision:** Normalized structure for core entities, JSONB for flexible metadata
- **Trade-off:** Better query performance vs. schema flexibility
- **Mitigation:** Use JSONB for truly flexible data only

### Embedded vs. Separate Provenance
- **Decision:** Hybrid approach (embedded for simple, separate for complex)
- **Trade-off:** Simpler queries vs. centralized provenance
- **Mitigation:** Clear guidelines for when to use each approach

### Hard vs. Soft Delete
- **Decision:** Soft delete for most entities, hard delete for temporary data
- **Trade-off:** Recovery capability vs. storage and query complexity
- **Mitigation:** Periodic cleanup of soft-deleted records

### Single vs. Multiple Schemas
- **Decision:** Single schema for core, separate schema for experimental
- **Trade-off:** Simpler vs. feature isolation
- **Mitigation:** Clear naming conventions for experimental features

## Next Steps After Approval

1. **Schema Review:** Technical review of proposed schema
2. **Decision Resolution:** Address schema decisions requiring human approval
3. **Environment Setup:** Set up PostgreSQL instance for testing
4. **Dry Run:** Execute migration on test data
5. **Performance Testing:** Validate with realistic data volumes
6. **Security Review:** Review security considerations and encryption needs
7. **Implementation Planning:** Detailed implementation timeline and resource planning
8. **Adapter Development:** Begin PostgreSQL storage adapter development

## Compliance with Constraints

✅ Database design and review task only  
✅ No runtime application behavior modified  
✅ No JSON storage deleted  
✅ No data migration executed  
✅ No database dependencies installed  
✅ No API behavior modified  
✅ No existing storage adapters removed  
✅ No deployment performed  
✅ No commits or pushes  

## Summary

The persistence architecture design provides a comprehensive PostgreSQL schema that:

1. **Separates Canonical and Derived Data:** Clear distinction with different retention policies
2. **Tracks Provenance:** Comprehensive provenance tracking for all derived data
3. **Ensures Data Safety:** Multiple validation checkpoints, rollback capability
4. **Supports Evolution:** Flexible schema design with JSONB and versioning
5. **Enables Performance:** Comprehensive indexing strategy for common query patterns
6. **Maintains Compatibility:** Future multi-user support through user_id fields
7. **Preserves Relationships:** Explicit relationship tables with referential integrity

The migration strategy ensures zero data loss with comprehensive validation and rollback capability. The design is ready for implementation upon approval of the schema decisions requiring human input.
