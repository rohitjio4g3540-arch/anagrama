# Persistence Architecture

> This document defines the PostgreSQL persistence architecture for Anagrama, emphasizing the separation of canonical and derived data for safe evolution and data preservation.

## Core Data Principle

**Original/canonical data must remain distinguishable from derived intelligence.**

The architecture conceptually separates data into three categories:

### 1. Canonical Data
Data that represents original, user-provided, or source information that should never be silently overwritten by derived intelligence.

**Examples:**
- Original sources (documents, files, web content)
- Uploaded files
- User-created memories
- Projects
- Decisions
- Tasks
- Explicitly provided preferences
- User classifications and labels

**Characteristics:**
- Immutable once created (or versioned with history)
- User-controlled modification
- High retention priority
- Strong provenance requirements
- Never automatically regenerated

### 2. Derived Data
Data that is generated or inferred by the system through processing, analysis, or AI operations.

**Examples:**
- AI summaries
- Embeddings
- Extracted concepts
- Entity extractions
- Classifications
- Inferred relationships
- Confidence scores
- Relevance rankings

**Characteristics:**
- Regenerable from canonical data
- May be versioned
- Can be safely recomputed
- Lower retention priority (can be regenerated)
- Must reference origin/sources
- May include generation metadata

### 3. Relationships and Provenance
Data that connects entities and tracks the origin and evolution of information.

**Examples:**
- source → memory relationships
- source → concept relationships
- memory → project relationships
- decision → evidence relationships
- entity → source relationships
- derivation chains (what derived this?)

**Characteristics:**
- Critical for attribution and verification
- Enable provenance traversal
- Support audit trails
- May have confidence weights
- Should be immutable or versioned

## Architecture Goals

### 1. Preservation Safety
- Derived information must not silently overwrite canonical information
- All modifications must be auditable
- Critical data must have backup/restore capability
- Deletion must consider dependencies

### 2. Attribution & Traceability
- Every derived record must reference its origin
- Generation methods must be recorded
- Model/provider information must be preserved
- Confidence levels must be tracked
- Version information must be maintained

### 3. Evolution Capability
- Schema must support future enhancements
- Migration paths must be safe
- Backward compatibility must be considered
- Experimental features must be isolatable

### 4. Query Performance
- Common query patterns must be optimized
- Indexing strategy must balance performance and storage
- Complex relationships must be traversable
- Scale must be considered from the start

## Data Classification Framework

### Canonical Data Tables
Tables that store original, user-provided, or source information:
- `users` - User accounts and preferences
- `projects` - Project definitions and metadata
- `sources` - Original content sources
- `source_files` - Uploaded file references
- `memories` - User-created memories
- `decisions` - User decisions with rationale
- `tasks` - User-defined tasks
- `user_preferences` - Explicit user preferences
- `classifications` - User-provided classifications

### Derived Data Tables
Tables that store generated or inferred information:
- `embeddings` - Vector embeddings
- `summaries` - AI-generated summaries
- `extracted_entities` - Entity extractions
- `extracted_concepts` - Concept extractions
- `classifications_auto` - Automatic classifications
- `relationships_inferred` - Inferred relationships
- `confidence_scores` - Computed confidence values
- `relevance_scores` - Computed relevance rankings

### Relationship Tables
Tables that connect entities and track provenance:
- `source_memory_links` - Source to memory relationships
- `source_concept_links` - Source to concept relationships
- `memory_project_links` - Memory to project relationships
- `decision_evidence_links` - Decision to evidence relationships
- `entity_source_links` - Entity to source relationships
- `derivation_chains` - What derived this record
- `provenance_records` - Comprehensive provenance tracking

## Provenance Model

### Provenance Requirements
Every derived record must preserve:
- **Origin Reference:** ID of the canonical source(s)
- **Creation Timestamp:** When was this derived?
- **Generation Method:** How was this derived? (extraction, classification, summarization, etc.)
- **Model/Provider:** Which AI model or algorithm generated this?
- **Parameters:** What parameters were used?
- **Confidence:** How confident is the system in this result?
- **Version:** Version of the generation method/model
- **Chain of Custody:** Complete derivation chain if applicable

### Provenance Implementation Strategies

#### Strategy 1: Embedded Provenance (Recommended for Simple Derivations)
Include provenance fields directly in derived tables:
```sql
CREATE TABLE embeddings (
    id UUID PRIMARY KEY,
    entity_id UUID NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    vector VECTOR(1536),
    model_used VARCHAR(100),
    model_version VARCHAR(50),
    generated_at TIMESTAMP,
    confidence FLOAT,
    -- provenance fields embedded
);
```

#### Strategy 2: Separate Provenance Table (Recommended for Complex Derivations)
Centralized provenance tracking:
```sql
CREATE TABLE provenance_records (
    id UUID PRIMARY KEY,
    derived_record_id UUID NOT NULL,
    derived_record_type VARCHAR(50) NOT NULL,
    origin_record_id UUID NOT NULL,
    origin_record_type VARCHAR(50) NOT NULL,
    generation_method VARCHAR(100),
    model_used VARCHAR(100),
    model_version VARCHAR(50),
    parameters JSONB,
    generated_at TIMESTAMP,
    confidence FLOAT,
    chain_of_custody UUID[], -- array of provenance record IDs
);
```

#### Strategy 3: Hybrid Approach (Recommended)
Use embedded provenance for simple derivations, separate table for complex chains.

## Mutability Strategy

### Immutable Tables
Tables that should never be modified after creation:
- `sources` - Original sources are immutable
- `source_files` - File references are immutable
- `decisions` - Decisions are immutable (create new to change)
- `provenance_records` - Provenance is immutable

### Versioned Tables
Tables that should track changes through versioning:
- `memories` - User may edit memories (track versions)
- `skills` - Skills may evolve (track versions)
- `classifications` - Classifications may be refined (track versions)

### Mutable Tables
Tables that are expected to change regularly:
- `projects` - Project metadata may change
- `tasks` - Task state changes frequently
- `user_preferences` - Preferences change over time
- `relationships` - Relationship confidence may change

### Soft Delete Strategy
Instead of hard deletes, use soft deletes with:
- `deleted_at TIMESTAMP` - When was this deleted?
- `deleted_by UUID` - Who/what deleted this?
- `deletion_reason TEXT` - Why was this deleted?
- `replaced_by UUID` - What record replaced this?

## Retention and Deletion Policy

### Canonical Data Retention
- **Sources:** Permanent retention (never auto-delete)
- **Memories:** Long-term retention with user-controlled deletion
- **Decisions:** Permanent retention (audit trail)
- **Projects:** Retain until explicitly deleted by user
- **Tasks:** Retain based on project policy or user preference

### Derived Data Retention
- **Embeddings:** Can be regenerated (shorter retention acceptable)
- **Summaries:** Can be regenerated (shorter retention acceptable)
- **Extractions:** Can be regenerated (shorter retention acceptable)
- **Classifications:** Can be regenerated (shorter retention acceptable)

### Cascade Deletion Rules
- Deleting a source should cascade to:
  - Soft delete derived embeddings
  - Soft delete extracted concepts
  - Soft delete inferred relationships
  - Keep provenance records for audit trail

- Deleting a memory should cascade to:
  - Soft delete memory embeddings
  - Soft delete memory relationships
  - Keep provenance records

### Dependency Tracking
Before deletion, check:
- What derived records depend on this?
- What relationships would be broken?
- Is this referenced in any decisions or tasks?
- Should user be prompted about dependencies?

## Performance Considerations

### Read Patterns
- **Project-scoped queries:** Most common, optimize with project_id indexes
- **Source lookup:** By ID, by project, by type, by date
- **Memory retrieval:** By project, by importance, by recency
- **Knowledge graph traversal:** Node and edge queries
- **Provenance traversal:** Following derivation chains

### Write Patterns
- **Source ingestion:** Batch writes, transactional
- **Memory creation:** Single writes, low frequency
- **Derived data generation:** Batch processing, may be async
- **Relationship updates:** Moderate frequency, transactional

### Indexing Strategy Principles
- Index foreign keys for JOIN performance
- Index query pattern columns (project_id, created_at, type)
- Use composite indexes for common multi-column queries
- Consider partial indexes for filtered queries
- Use BRIN indexes for time-series data
- Use GIN indexes for JSONB and array columns
- Plan for pgvector HNSW indexes for semantic search

## Schema Evolution Strategy

### Version Control
- Track schema version in a `schema_migrations` table
- Use migration scripts with up/down methods
- Test migrations on copy of production data
- Maintain rollback capability

### Backward Compatibility
- Add columns with default values
- Use views for API compatibility during transitions
- Deprecate old columns before removal
- Maintain adapter layer for application compatibility

### Experimental Features
- Use separate schemas for experimental features
- Isolate experimental tables from core schema
- Easy to drop experimental features
- Clear naming conventions (experimental_*)

## Security Considerations

### Data Access Control
- Row-level security for multi-user future
- Project-based access control
- Sensitive data encryption at rest
- API key encryption in database

### Audit Trail
- Log all modifications to canonical data
- Track who/what made changes
- Maintain change history for critical tables
- Immutable audit log for security events

### Backup Strategy
- Regular full backups
- Point-in-time recovery capability
- Backup before schema migrations
- Test restore procedures regularly

## Open Questions

1. **Versioning Granularity:** Should all user-editable content be versioned, or just specific types?
2. **Provenance Storage:** Embedded vs. separate table vs. hybrid approach?
3. **Derived Data Retention:** What is the optimal retention policy for embeddings and extractions?
4. **Cascade Deletion:** Should cascade deletes be automatic or require user confirmation?
5. **Soft Delete Retention:** How long should soft-deleted records be retained?
6. **Large Object Storage:** Should file content be stored in database or external object storage?
7. **JSONB vs. Separate Tables:** When to use JSONB vs. normalized tables for metadata?
8. **Temporal Validity:** How to track time-valid relationships (e.g., "worked at" relationships)?

## Trade-offs

### Normalization vs. JSONB
- **Normalization:** Better query performance, stricter schema, more joins
- **JSONB:** Flexible schema, fewer joins, slower complex queries
- **Decision:** Use normalized structure for core entities, JSONB for flexible metadata

### Embedded vs. Separate Provenance
- **Embedded:** Simpler queries, less joins, provenance scattered
- **Separate:** Centralized provenance, more joins, complex queries
- **Decision:** Hybrid approach - embedded for simple derivations, separate for complex chains

### Hard vs. Soft Delete
- **Hard Delete:** Simpler, less storage, permanent data loss
- **Soft Delete:** Recovery possible, more storage, complex queries
- **Decision:** Soft delete for most entities, hard delete for temporary/derived data

### Single vs. Multiple Schemas
- **Single Schema:** Simpler, monolithic, harder to isolate features
- **Multiple Schemas:** Feature isolation, more complex, better organization
- **Decision:** Single schema for core, separate schema for experimental features

## Next Steps

1. **Detailed Schema Design:** Create specific table definitions with all fields
2. **ERD Creation:** Visual representation of entity relationships
3. **Migration Planning:** Specific migration scripts from JSON to PostgreSQL
4. **Indexing Design:** Detailed index specifications
5. **Performance Testing:** Validate design with realistic data volumes
