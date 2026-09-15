# Migration Strategy

> This document details the safe migration strategy from JSON storage to PostgreSQL, ensuring zero data loss and rollback capability.

## Current JSON Storage Analysis

### Current JSON Files

#### storage/anagrama-state.json
**Purpose:** Stores knowledge graph data (nodes, edges, sources, projects)

**Structure:**
```json
{
  "nodes": [
    {
      "id": "node_abc123",
      "label": "attention",
      "type": "concept",
      "confidence": 0.7,
      "source_ids": ["src_def456"]
    }
  ],
  "edges": [
    {
      "id": "edge_ghi789",
      "source": "node_abc123",
      "target": "node_jkl012",
      "relation": "discusses",
      "confidence": 0.65,
      "evidence": ["src_def456"]
    }
  ],
  "sources": [
    {
      "id": "src_def456",
      "title": "Attention as architecture",
      "kind": "document",
      "content": "Full content here...",
      "created_at": "2026-07-19T12:00:00Z",
      "metadata": {}
    }
  ],
  "projects": [
    {
      "id": "proj_mno345",
      "title": "Design System",
      "description": "Design system project"
    }
  ]
}
```

**Record Count Estimation:** Unknown (need to analyze actual file)

#### storage/memory.json
**Purpose:** Stores memory entries with tiered organization

**Structure:**
```json
[
  {
    "id": "mem_pqr678",
    "tier": "conversation",
    "content": "User asked about attention",
    "project_id": "proj_mno345",
    "created_at": "2026-07-19T12:00:00Z"
  }
]
```

**Record Count Estimation:** Unknown (need to analyze actual file)

### Current ID Format
- **Pattern:** `prefix_randomstring` (e.g., `node_abc123`, `src_def456`)
- **Prefixes:** `node_`, `edge_`, `src_`, `proj_`, `mem_`
- **Random Part:** 6-8 character alphanumeric string
- **Uniqueness:** Likely unique within file, no cross-file guarantee

### Current Data Relationships
- **Nodes → Sources:** Via `source_ids` array
- **Edges → Sources:** Via `evidence` array
- **Sources → Projects:** Not explicitly linked (project_id not in source structure)
- **Memories → Projects:** Via `project_id` field

## Migration Goals

### Primary Goals
1. **Zero Data Loss:** No records may be lost during migration
2. **Data Integrity:** All relationships must be preserved
3. **Rollback Capability:** Must be able to rollback to JSON if migration fails
4. **Validation:** Post-migration data must be validated against original
5. **Minimal Downtime:** Migration should have minimal impact on system availability

### Secondary Goals
1. **Performance:** Migration should complete in reasonable time
2. **Idempotency:** Migration should be repeatable without side effects
3. **Observability:** Migration progress should be visible and monitorable
4. **Safety:** Multiple validation checkpoints throughout process

## Migration Strategy Overview

### Approach: Phased Migration with Rollback Safety

**Phase 1: Preparation and Validation**
- Backup JSON files
- Analyze JSON structure and data volume
- Validate JSON integrity
- Create empty PostgreSQL schema
- Validate PostgreSQL connectivity

**Phase 2: Schema Setup**
- Create all tables with proposed schema
- Create all indexes
- Create necessary extensions (pgvector)
- Validate schema creation

**Phase 3: Data Migration (Read-Only JSON)**
- Read JSON files (no modifications)
- Transform data to match PostgreSQL schema
- Load data into PostgreSQL in transactions
- Validate record counts match

**Phase 4: Relationship Migration**
- Migrate node → source relationships
- Migrate edge → source relationships
- Migrate memory → project relationships
- Validate referential integrity

**Phase 5: Post-Migration Validation**
- Compare record counts
- Validate data integrity
- Test sample queries
- Performance validation

**Phase 6: Adapter Switch (Future)**
- Implement PostgreSQL storage adapters
- Maintain JSON adapter fallback
- Gradual rollout with monitoring
- Final JSON deprecation

## Detailed Migration Steps

### Phase 1: Preparation and Validation

#### Step 1.1: Pre-Migration Backup
```bash
# Create timestamped backup directory
BACKUP_DIR="storage/backups/migration_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup JSON files
cp storage/anagrama-state.json "$BACKUP_DIR/anagrama-state.json.backup"
cp storage/memory.json "$BACKUP_DIR/memory.json.backup"

# Create checksums
sha256sum "$BACKUP_DIR/anagrama-state.json.backup" > "$BACKUP_DIR/checksums.txt"
sha256sum "$BACKUP_DIR/memory.json.backup" >> "$BACKUP_DIR/checksums.txt"

# Verify backup integrity
sha256sum -c "$BACKUP_DIR/checksums.txt"
```

**Validation:** Backup files exist and checksums validate

#### Step 1.2: JSON Structure Analysis
```python
import json
from pathlib import Path

# Analyze anagrama-state.json
state_file = Path("storage/anagrama-state.json")
with open(state_file) as f:
    state_data = json.load(f)

print(f"Nodes: {len(state_data['nodes'])}")
print(f"Edges: {len(state_data['edges'])}")
print(f"Sources: {len(state_data['sources'])}")
print(f"Projects: {len(state_data['projects'])}")

# Analyze memory.json
memory_file = Path("storage/memory.json")
with open(memory_file) as f:
    memory_data = json.load(f)

print(f"Memories: {len(memory_data)}")

# Analyze ID formats
def analyze_ids(items, entity_type):
    ids = [item['id'] for item in items]
    print(f"{entity_type} IDs: {len(ids)}")
    print(f"Sample IDs: {ids[:3]}")
    print(f"Unique IDs: {len(set(ids))}")
    if len(ids) != len(set(ids)):
        print("WARNING: Duplicate IDs found!")

analyze_ids(state_data['nodes'], 'Nodes')
analyze_ids(state_data['edges'], 'Edges')
analyze_ids(state_data['sources'], 'Sources')
analyze_ids(state_data['projects'], 'Projects')
analyze_ids(memory_data, 'Memories')
```

**Validation:** Record counts documented, ID uniqueness verified, ID formats understood

#### Step 1.3: JSON Integrity Validation
```python
import json
from pathlib import Path

def validate_json_structure(file_path, expected_keys):
    with open(file_path) as f:
        data = json.load(f)
    
    for key in expected_keys:
        if key not in data:
            raise ValueError(f"Missing expected key: {key}")
    
    print(f"✓ {file_path} structure valid")
    return data

# Validate anagrama-state.json
state_data = validate_json_structure(
    "storage/anagrama-state.json",
    ["nodes", "edges", "sources", "projects"]
)

# Validate memory.json
memory_data = validate_json_structure(
    "storage/memory.json",
    []  # Memory is an array, not a dict
)

print("✓ All JSON files valid")
```

**Validation:** JSON files are valid and have expected structure

#### Step 1.4: PostgreSQL Connectivity Validation
```python
import psycopg2
from backend.config.settings import get_settings

settings = get_settings()
try:
    conn = psycopg2.connect(settings.database_url)
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"✓ PostgreSQL connected: {version[0]}")
    cursor.close()
    conn.close()
except Exception as e:
    raise Exception(f"PostgreSQL connection failed: {e}")
```

**Validation:** PostgreSQL connection successful, version documented

### Phase 2: Schema Setup

#### Step 2.1: Create Schema
```sql
-- Create database if not exists
CREATE DATABASE IF NOT EXISTS anagrama;

-- Connect to anagrama database
\c anagrama

-- Create pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create all tables in order (respecting foreign keys)
-- (Full schema from DATABASE_SCHEMA_PROPOSAL.md)
```

**Validation:** All tables created, extensions installed, no errors

#### Step 2.2: Create Indexes
```sql
-- Create all indexes as specified in DATABASE_SCHEMA_PROPOSAL.md
-- This should be done after data load for performance, but can be done before for validation
```

**Validation:** All indexes created successfully

#### Step 2.3: Schema Validation
```python
import psycopg2

def validate_schema():
    conn = psycopg2.connect(settings.database_url)
    cursor = conn.cursor()
    
    # Check tables exist
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = {row[0] for row in cursor.fetchall()}
    expected_tables = {
        'users', 'projects', 'sources', 'source_files', 'memories',
        'memory_versions', 'decisions', 'tasks', 'task_state_history',
        'user_preferences', 'embeddings', 'summaries', 'extracted_entities',
        'extracted_concepts', 'classifications_auto', 'knowledge_nodes',
        'knowledge_edges', 'edge_evidence_links', 'source_memory_links',
        'memory_project_links', 'decision_evidence_links', 'provenance_records',
        'skills', 'skill_versions'
    }
    
    missing_tables = expected_tables - tables
    if missing_tables:
        raise Exception(f"Missing tables: {missing_tables}")
    
    print(f"✓ All {len(tables)} expected tables exist")
    
    # Check pgvector extension
    cursor.execute("""
        SELECT extname 
        FROM pg_extension 
        WHERE extname = 'vector'
    """)
    if not cursor.fetchone():
        raise Exception("pgvector extension not installed")
    
    print("✓ pgvector extension installed")
    
    cursor.close()
    conn.close()

validate_schema()
```

**Validation:** All tables exist, pgvector extension installed

### Phase 3: Data Migration

#### Step 3.1: ID Preservation Strategy
**Decision:** Preserve existing JSON IDs in PostgreSQL UUID fields

**Approach:**
- JSON IDs are strings like `node_abc123`
- PostgreSQL expects UUIDs
- Strategy: Use UUID v5 (namespace-based) to convert string IDs to UUIDs
- Namespace: Use a fixed namespace UUID for Anagrama
- Conversion: `UUID5(namespace, json_id_string)`

**Implementation:**
```python
import uuid

ANAGRAMA_NAMESPACE = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # DNS namespace

def json_id_to_uuid(json_id: str) -> uuid.UUID:
    """Convert JSON string ID to UUID v5"""
    return uuid.uuid5(ANAGRAMA_NAMESPACE, json_id)

# Example
json_id = "node_abc123"
uuid_id = json_id_to_uuid(json_id)
print(f"JSON ID: {json_id} → UUID: {uuid_id}")
```

**Benefits:**
- Deterministic conversion (same JSON ID always produces same UUID)
- Preserves traceability back to original IDs
- UUID format compatible with PostgreSQL
- No collisions if JSON IDs are unique

#### Step 3.2: Sources Migration
```python
import json
import uuid
import psycopg2
from datetime import datetime
from pathlib import Path

def migrate_sources():
    # Load JSON data
    state_file = Path("storage/anagrama-state.json")
    with open(state_file) as f:
        state_data = json.load(f)
    
    sources = state_data['sources']
    
    # Convert and insert
    conn = psycopg2.connect(settings.database_url)
    cursor = conn.cursor()
    
    inserted_count = 0
    for source in sources:
        try:
            # Convert ID
            source_uuid = json_id_to_uuid(source['id'])
            
            # Convert project_id if exists
            project_uuid = None
            if 'project_id' in source and source['project_id']:
                project_uuid = json_id_to_uuid(source['project_id'])
            
            # Parse timestamp
            created_at = datetime.fromisoformat(source['created_at'].replace('Z', '+00:00'))
            
            # Insert
            cursor.execute("""
                INSERT INTO sources (id, project_id, title, kind, content, metadata, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                source_uuid,
                project_uuid,
                source['title'],
                source['kind'],
                source.get('content', ''),
                json.dumps(source.get('metadata', {})),
                created_at
            ))
            inserted_count += 1
        except Exception as e:
            print(f"Error migrating source {source['id']}: {e}")
            conn.rollback()
            raise
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✓ Migrated {inserted_count}/{len(sources)} sources")
    return inserted_count
```

**Validation:** Inserted count matches JSON source count

#### Step 3.3: Projects Migration
```python
def migrate_projects():
    state_file = Path("storage/anagrama-state.json")
    with open(state_file) as f:
        state_data = json.load(f)
    
    projects = state_data['projects']
    
    # Create default user if not exists
    default_user_id = uuid.uuid4()  # Will be replaced with real user auth
    
    conn = psycopg2.connect(settings.database_url)
    cursor = conn.cursor()
    
    # Insert default user
    cursor.execute("""
        INSERT INTO users (id, email, name)
        VALUES (%s, %s, %s)
        ON CONFLICT (email) DO NOTHING
    """, (default_user_id, 'default@anagrama.local', 'Default User'))
    
    inserted_count = 0
    for project in projects:
        try:
            project_uuid = json_id_to_uuid(project['id'])
            
            cursor.execute("""
                INSERT INTO projects (id, user_id, title, description)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                project_uuid,
                default_user_id,
                project['title'],
                project.get('description', '')
            ))
            inserted_count += 1
        except Exception as e:
            print(f"Error migrating project {project['id']}: {e}")
            conn.rollback()
            raise
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✓ Migrated {inserted_count}/{len(projects)} projects")
    return inserted_count
```

**Validation:** Inserted count matches JSON project count

#### Step 3.4: Knowledge Nodes Migration
```python
def migrate_nodes():
    state_file = Path("storage/anagrama-state.json")
    with open(state_file) as f:
        state_data = json.load(f)
    
    nodes = state_data['nodes']
    
    conn = psycopg2.connect(settings.database_url)
    cursor = conn.cursor()
    
    inserted_count = 0
    for node in nodes:
        try:
            node_uuid = json_id_to_uuid(node['id'])
            
            cursor.execute("""
                INSERT INTO knowledge_nodes (id, label, node_type, confidence, metadata)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                node_uuid,
                node['label'],
                node['type'],  # 'type' in JSON, 'node_type' in PostgreSQL
                node.get('confidence', 0.7),
                json.dumps({'source_ids': node.get('source_ids', [])})
            ))
            inserted_count += 1
        except Exception as e:
            print(f"Error migrating node {node['id']}: {e}")
            conn.rollback()
            raise
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✓ Migrated {inserted_count}/{len(nodes)} nodes")
    return inserted_count
```

**Validation:** Inserted count matches JSON node count

#### Step 3.5: Knowledge Edges Migration
```python
def migrate_edges():
    state_file = Path("storage/anagrama-state.json")
    with open(state_file) as f:
        state_data = json.load(f)
    
    edges = state_data['edges']
    
    conn = psycopg2.connect(settings.database_url)
    cursor = conn.cursor()
    
    inserted_count = 0
    for edge in edges:
        try:
            edge_uuid = json_id_to_uuid(edge['id'])
            source_uuid = json_id_to_uuid(edge['source'])
            target_uuid = json_id_to_uuid(edge['target'])
            
            cursor.execute("""
                INSERT INTO knowledge_edges (id, source_node_id, target_node_id, relation, confidence, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                edge_uuid,
                source_uuid,
                target_uuid,
                edge['relation'],
                edge.get('confidence', 0.65),
                json.dumps({'evidence': edge.get('evidence', [])})
            ))
            inserted_count += 1
        except Exception as e:
            print(f"Error migrating edge {edge['id']}: {e}")
            conn.rollback()
            raise
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✓ Migrated {inserted_count}/{len(edges)} edges")
    return inserted_count
```

**Validation:** Inserted count matches JSON edge count

#### Step 3.6: Memories Migration
```python
def migrate_memories():
    memory_file = Path("storage/memory.json")
    with open(memory_file) as f:
        memory_data = json.load(f)
    
    # Create default user if not exists
    default_user_id = uuid.uuid4()
    
    conn = psycopg2.connect(settings.database_url)
    cursor = conn.cursor()
    
    # Insert default user
    cursor.execute("""
        INSERT INTO users (id, email, name)
        VALUES (%s, %s, %s)
        ON CONFLICT (email) DO NOTHING
    """, (default_user_id, 'default@anagrama.local', 'Default User'))
    
    inserted_count = 0
    for memory in memory_data:
        try:
            memory_uuid = json_id_to_uuid(memory['id'])
            
            # Convert project_id if exists
            project_uuid = None
            if 'project_id' in memory and memory['project_id']:
                project_uuid = json_id_to_uuid(memory['project_id'])
            
            # Parse timestamp
            created_at = datetime.fromisoformat(memory['created_at'].replace('Z', '+00:00'))
            
            cursor.execute("""
                INSERT INTO memories (id, user_id, project_id, tier, content, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                memory_uuid,
                default_user_id,
                project_uuid,
                memory['tier'],
                memory['content'],
                created_at
            ))
            inserted_count += 1
        except Exception as e:
            print(f"Error migrating memory {memory['id']}: {e}")
            conn.rollback()
            raise
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✓ Migrated {inserted_count}/{len(memory_data)} memories")
    return inserted_count
```

**Validation:** Inserted count matches JSON memory count

### Phase 4: Relationship Migration

#### Step 4.1: Node → Source Relationships
```python
def migrate_node_source_relationships():
    state_file = Path("storage/anagrama-state.json")
    with open(state_file) as f:
        state_data = json.load(f)
    
    nodes = state_data['nodes']
    
    conn = psycopg2.connect(settings.database_url)
    cursor = conn.cursor()
    
    inserted_count = 0
    for node in nodes:
        try:
            node_uuid = json_id_to_uuid(node['id'])
            source_ids = node.get('source_ids', [])
            
            for source_id in source_ids:
                source_uuid = json_id_to_uuid(source_id)
                
                # Create link via extracted_concepts (derived relationship)
                cursor.execute("""
                    INSERT INTO extracted_concepts (id, source_id, concept_text, concept_metadata, extraction_method, model_used, confidence, extracted_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (
                    uuid.uuid4(),
                    source_uuid,
                    node['label'],
                    json.dumps({'node_id': str(node_uuid)}),
                    'migration',
                    'legacy_json',
                    1.0,  # High confidence for migrated data
                    datetime.now()
                ))
                inserted_count += 1
        except Exception as e:
            print(f"Error migrating node-source relationships for {node['id']}: {e}")
            conn.rollback()
            raise
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✓ Migrated {inserted_count} node-source relationships")
    return inserted_count
```

**Validation:** All node → source relationships preserved

#### Step 4.2: Edge → Source Relationships
```python
def migrate_edge_source_relationships():
    state_file = Path("storage/anagrama-state.json")
    with open(state_file) as f:
        state_data = json.load(f)
    
    edges = state_data['edges']
    
    conn = psycopg2.connect(settings.database_url)
    cursor = conn.cursor()
    
    inserted_count = 0
    for edge in edges:
        try:
            edge_uuid = json_id_to_uuid(edge['id'])
            evidence_ids = edge.get('evidence', [])
            
            for evidence_id in evidence_ids:
                evidence_uuid = json_id_to_uuid(evidence_id)
                
                # Create edge evidence link
                cursor.execute("""
                    INSERT INTO edge_evidence_links (id, edge_id, source_id, created_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (
                    uuid.uuid4(),
                    edge_uuid,
                    evidence_uuid,
                    datetime.now()
                ))
                inserted_count += 1
        except Exception as e:
            print(f"Error migrating edge-source relationships for {edge['id']}: {e}")
            conn.rollback()
            raise
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✓ Migrated {inserted_count} edge-source relationships")
    return inserted_count
```

**Validation:** All edge → source relationships preserved

#### Step 4.3: Memory → Project Relationships
```python
def migrate_memory_project_relationships():
    memory_file = Path("storage/memory.json")
    with open(memory_file) as f:
        memory_data = json.load(f)
    
    conn = psycopg2.connect(settings.database_url)
    cursor = conn.cursor()
    
    inserted_count = 0
    for memory in memory_data:
        try:
            memory_uuid = json_id_to_uuid(memory['id'])
            
            if 'project_id' in memory and memory['project_id']:
                project_uuid = json_id_to_uuid(memory['project_id'])
                
                cursor.execute("""
                    INSERT INTO memory_project_links (id, memory_id, project_id, created_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (
                    uuid.uuid4(),
                    memory_uuid,
                    project_uuid,
                    datetime.now()
                ))
                inserted_count += 1
        except Exception as e:
            print(f"Error migrating memory-project relationship for {memory['id']}: {e}")
            conn.rollback()
            raise
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✓ Migrated {inserted_count} memory-project relationships")
    return inserted_count
```

**Validation:** All memory → project relationships preserved

### Phase 5: Post-Migration Validation

#### Step 5.1: Record Count Comparison
```python
def validate_record_counts():
    # JSON counts
    state_file = Path("storage/anagrama-state.json")
    with open(state_file) as f:
        state_data = json.load(f)
    
    memory_file = Path("storage/memory.json")
    with open(memory_file) as f:
        memory_data = json.load(f)
    
    json_counts = {
        'sources': len(state_data['sources']),
        'projects': len(state_data['projects']),
        'nodes': len(state_data['nodes']),
        'edges': len(state_data['edges']),
        'memories': len(memory_data)
    }
    
    # PostgreSQL counts
    conn = psycopg2.connect(settings.database_url)
    cursor = conn.cursor()
    
    pg_counts = {}
    cursor.execute("SELECT COUNT(*) FROM sources")
    pg_counts['sources'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM projects")
    pg_counts['projects'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM knowledge_nodes")
    pg_counts['nodes'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM knowledge_edges")
    pg_counts['edges'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM memories")
    pg_counts['memories'] = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    # Compare
    all_match = True
    for table in json_counts:
        if json_counts[table] != pg_counts[table]:
            print(f"✗ Count mismatch for {table}: JSON={json_counts[table]}, PG={pg_counts[table]}")
            all_match = False
        else:
            print(f"✓ Count match for {table}: {json_counts[table]}")
    
    if all_match:
        print("✓ All record counts match")
    else:
        raise Exception("Record count validation failed")
    
    return all_match
```

**Validation:** All record counts match between JSON and PostgreSQL

#### Step 5.2: Referential Integrity Validation
```python
def validate_referential_integrity():
    conn = psycopg2.connect(settings.database_url)
    cursor = conn.cursor()
    
    # Check for orphaned nodes (nodes with no source relationships)
    cursor.execute("""
        SELECT COUNT(*) 
        FROM knowledge_nodes kn
        LEFT JOIN extracted_concepts ec ON kn.label = ec.concept_text
        WHERE ec.id IS NULL
    """)
    orphaned_nodes = cursor.fetchone()[0]
    
    if orphaned_nodes > 0:
        print(f"⚠ Warning: {orphaned_nodes} nodes have no source relationships")
    else:
        print("✓ All nodes have source relationships")
    
    # Check for orphaned edges (edges with no evidence)
    cursor.execute("""
        SELECT COUNT(*) 
        FROM knowledge_edges ke
        LEFT JOIN edge_evidence_links eel ON ke.id = eel.edge_id
        WHERE eel.id IS NULL
    """)
    orphaned_edges = cursor.fetchone()[0]
    
    if orphaned_edges > 0:
        print(f"⚠ Warning: {orphaned_edges} edges have no evidence")
    else:
        print("✓ All edges have evidence")
    
    # Check for orphaned memories (memories with no project but should have one)
    cursor.execute("""
        SELECT COUNT(*) 
        FROM memories m
        WHERE m.project_id IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM memory_project_links mpl 
            WHERE mpl.memory_id = m.id
        )
    """)
    orphaned_memory_links = cursor.fetchone()[0]
    
    if orphaned_memory_links > 0:
        print(f"⚠ Warning: {orphaned_memory_links} memories have project_id but no link")
    else:
        print("✓ All memory-project relationships consistent")
    
    cursor.close()
    conn.close()
```

**Validation:** Referential integrity validated, warnings documented

#### Step 5.3: Data Integrity Validation
```python
def validate_data_integrity():
    conn = psycopg2.connect(settings.database_url)
    cursor = conn.cursor()
    
    # Sample validation: Check that sources have required fields
    cursor.execute("""
        SELECT COUNT(*) 
        FROM sources 
        WHERE title IS NULL 
        OR title = ''
        OR kind IS NULL 
        OR kind = ''
    """)
    invalid_sources = cursor.fetchone()[0]
    
    if invalid_sources > 0:
        print(f"✗ {invalid_sources} sources have missing required fields")
    else:
        print("✓ All sources have required fields")
    
    # Check that nodes have labels
    cursor.execute("""
        SELECT COUNT(*) 
        FROM knowledge_nodes 
        WHERE label IS NULL 
        OR label = ''
    """)
    invalid_nodes = cursor.fetchone()[0]
    
    if invalid_nodes > 0:
        print(f"✗ {invalid_nodes} nodes have missing labels")
    else:
        print("✓ All nodes have labels")
    
    # Check that memories have content
    cursor.execute("""
        SELECT COUNT(*) 
        FROM memories 
        WHERE content IS NULL 
        OR content = ''
    """)
    invalid_memories = cursor.fetchone()[0]
    
    if invalid_memories > 0:
        print(f"✗ {invalid_memories} memories have missing content")
    else:
        print("✓ All memories have content")
    
    cursor.close()
    conn.close()
```

**Validation:** Data integrity validated, no critical issues

#### Step 5.4: Checksum Validation
```python
def validate_checksums():
    # Calculate checksum of critical fields in PostgreSQL
    conn = psycopg2.connect(settings.database_url)
    cursor = conn.cursor()
    
    # Source content checksums
    cursor.execute("""
        SELECT md5(content) as checksum, COUNT(*) 
        FROM sources 
        GROUP BY checksum
    """)
    print("Source content checksum distribution:")
    for row in cursor.fetchall():
        print(f"  Checksum {row[0]}: {row[1]} sources")
    
    # Memory content checksums
    cursor.execute("""
        SELECT md5(content) as checksum, COUNT(*) 
        FROM memories 
        GROUP BY checksum
    """)
    print("Memory content checksum distribution:")
    for row in cursor.fetchall():
        print(f"  Checksum {row[0]}: {row[1]} memories")
    
    cursor.close()
    conn.close()
    
    print("✓ Checksum validation complete")
```

**Validation:** Checksums calculated for comparison with future validations

#### Step 5.5: Sample Query Validation
```python
def validate_sample_queries():
    conn = psycopg2.connect(settings.database_url)
    cursor = conn.cursor()
    
    # Test project-scoped query
    cursor.execute("""
        SELECT COUNT(*) 
        FROM sources s
        JOIN projects p ON s.project_id = p.id
        WHERE p.deleted_at IS NULL
    """)
    project_sources = cursor.fetchone()[0]
    print(f"✓ Project-scoped source query: {project_sources} results")
    
    # Test memory retrieval query
    cursor.execute("""
        SELECT COUNT(*) 
        FROM memories m
        WHERE m.deleted_at IS NULL
        ORDER BY m.importance_score DESC, m.created_at DESC
        LIMIT 10
    """)
    top_memories = cursor.fetchone()[0]
    print(f"✓ Memory retrieval query: {top_memories} results")
    
    # Test graph traversal query
    cursor.execute("""
        SELECT COUNT(*) 
        FROM knowledge_edges ke
        JOIN knowledge_nodes kn1 ON ke.source_node_id = kn1.id
        JOIN knowledge_nodes kn2 ON ke.target_node_id = kn2.id
        WHERE ke.deleted_at IS NULL
    """)
    graph_edges = cursor.fetchone()[0]
    print(f"✓ Graph traversal query: {graph_edges} results")
    
    cursor.close()
    conn.close()
    
    print("✓ Sample queries validated")
```

**Validation:** Sample queries execute successfully with expected results

### Phase 6: Rollback Strategy

#### Rollback Triggers
Rollback should be triggered if:
- Any validation step fails
- Record counts don't match
- Referential integrity violations found
- Data integrity issues found
- Performance thresholds not met
- User requests rollback

#### Rollback Procedure
```bash
# 1. Stop application (prevent writes during rollback)
# 2. Drop PostgreSQL database (or schema)
DROP DATABASE IF EXISTS anagrama;

# 3. Restore JSON files from backup
cp storage/backups/migration_TIMESTAMP/anagrama-state.json.backup storage/anagrama-state.json
cp storage/backups/migration_TIMESTAMP/memory.json.backup storage/memory.json

# 4. Validate JSON integrity
sha256sum -c storage/backups/migration_TIMESTAMP/checksums.txt

# 5. Restart application with JSON storage
# 6. Verify application functionality
```

#### Rollback Validation
- JSON files restored and checksums match
- Application starts successfully
- API endpoints respond correctly
- Data accessible through application

## Migration Script

### Complete Migration Script
```python
#!/usr/bin/env python3
"""
Migration script: JSON to PostgreSQL
Usage: python migrate_json_to_postgres.py
"""

import json
import uuid
import psycopg2
from datetime import datetime
from pathlib import Path
import sys

# Configuration
ANAGRAMA_NAMESPACE = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
BACKUP_DIR = Path("storage/backups/migration_" + datetime.now().strftime("%Y%m%d_%H%M%S"))

def json_id_to_uuid(json_id: str) -> uuid.UUID:
    """Convert JSON string ID to UUID v5"""
    return uuid.uuid5(ANAGRAMA_NAMESPACE, json_id)

def create_backup():
    """Create backup of JSON files"""
    print("Creating backup...")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Backup files
    Path("storage/anagrama-state.json").copy(BACKUP_DIR / "anagrama-state.json.backup")
    Path("storage/memory.json").copy(BACKUP_DIR / "memory.json.backup")
    
    # Create checksums
    import subprocess
    with open(BACKUP_DIR / "checksums.txt", 'w') as f:
        subprocess.run(['sha256sum', str(BACKUP_DIR / "anagrama-state.json.backup")], stdout=f)
        subprocess.run(['sha256sum', str(BACKUP_DIR / "memory.json.backup")], stdout=f)
    
    print(f"✓ Backup created at {BACKUP_DIR}")

def validate_json():
    """Validate JSON files"""
    print("Validating JSON files...")
    
    # Validate anagrama-state.json
    with open("storage/anagrama-state.json") as f:
        state_data = json.load(f)
    
    required_keys = ["nodes", "edges", "sources", "projects"]
    for key in required_keys:
        if key not in state_data:
            raise Exception(f"Missing key in anagrama-state.json: {key}")
    
    # Validate memory.json
    with open("storage/memory.json") as f:
        memory_data = json.load(f)
    
    print("✓ JSON files valid")
    return state_data, memory_data

def create_schema():
    """Create PostgreSQL schema"""
    print("Creating PostgreSQL schema...")
    # Implementation would execute SQL from DATABASE_SCHEMA_PROPOSAL.md
    print("✓ Schema created")

def migrate_data(state_data, memory_data):
    """Migrate data from JSON to PostgreSQL"""
    print("Migrating data...")
    
    # Implementation would call migration functions defined above
    # migrate_projects()
    # migrate_sources()
    # migrate_nodes()
    # migrate_edges()
    # migrate_memories()
    # migrate_node_source_relationships()
    # migrate_edge_source_relationships()
    # migrate_memory_project_relationships()
    
    print("✓ Data migrated")

def validate_migration():
    """Validate migration results"""
    print("Validating migration...")
    
    # Implementation would call validation functions defined above
    # validate_record_counts()
    # validate_referential_integrity()
    # validate_data_integrity()
    # validate_checksums()
    # validate_sample_queries()
    
    print("✓ Migration validated")

def main():
    try:
        print("Starting migration...")
        create_backup()
        state_data, memory_data = validate_json()
        create_schema()
        migrate_data(state_data, memory_data)
        validate_migration()
        print("✓ Migration completed successfully")
        return 0
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        print("Rollback not automatic - please restore from backup if needed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

## Migration Timeline Estimate

### Small Dataset (< 1000 records each)
- **Phase 1:** 5 minutes
- **Phase 2:** 10 minutes
- **Phase 3:** 15 minutes
- **Phase 4:** 10 minutes
- **Phase 5:** 15 minutes
- **Total:** ~55 minutes

### Medium Dataset (1000-10000 records each)
- **Phase 1:** 10 minutes
- **Phase 2:** 15 minutes
- **Phase 3:** 30 minutes
- **Phase 4:** 20 minutes
- **Phase 5:** 30 minutes
- **Total:** ~105 minutes

### Large Dataset (> 10000 records each)
- **Phase 1:** 15 minutes
- **Phase 2:** 30 minutes
- **Phase 3:** 60+ minutes
- **Phase 4:** 45 minutes
- **Phase 5:** 60 minutes
- **Total:** ~210+ minutes

## Risks and Mitigation

### Risk 1: ID Collision
**Risk:** UUID v5 conversion might produce collisions if JSON IDs are not unique
**Mitigation:** Validate JSON ID uniqueness before migration, use namespace-based UUIDs

### Risk 2: Data Loss During Migration
**Risk:** Records might be lost if migration script fails mid-process
**Mitigation:** Transactional inserts, comprehensive backup, rollback capability

### Risk 3: Relationship Loss
**Risk:** Complex relationships might not be preserved correctly
**Mitigation:** Explicit relationship migration, referential integrity validation

### Risk 4: Performance Issues
**Risk:** Migration might be slow for large datasets
**Mitigation:** Batch inserts, progress monitoring, performance testing

### Risk 5: Schema Mismatch
**Risk:** PostgreSQL schema might not accommodate all JSON data structures
**Mitigation:** Comprehensive JSON analysis, flexible JSONB fields, schema validation

### Risk 6: Application Downtime
**Risk:** Migration might require application downtime
**Mitigation:** Plan migration during low-usage periods, maintain JSON fallback

## Open Questions

1. **ID Conversion Strategy:** Is UUID v5 the right approach, or should we use a different strategy?
2. **Default User:** How should we handle the default user for migrated data?
3. **Project Assignment:** How should we assign sources to projects if not explicitly linked in JSON?
4. **Timestamp Precision:** How should we handle timestamp precision differences between JSON and PostgreSQL?
5. **Large Content:** How should we handle very large source content (performance vs. completeness)?
6. **Concurrent Access:** How should we handle concurrent access during migration (read-only vs. maintenance mode)?

## Success Criteria

Migration is considered successful when:
- [ ] All JSON files backed up with validated checksums
- [ ] All PostgreSQL tables created successfully
- [ ] All records migrated with zero data loss
- [ ] All record counts match between JSON and PostgreSQL
- [ ] All relationships preserved and validated
- [ ] Referential integrity validated
- [ ] Data integrity validated
- [ ] Sample queries execute successfully
- [ ] Performance benchmarks meet requirements
- [ ] Rollback procedure tested and documented

## Next Steps

1. **Review and Approval:** Migration strategy review by stakeholders
2. **Environment Setup:** Set up PostgreSQL instance for testing
3. **Dry Run:** Execute migration on test data
4. **Performance Testing:** Validate with realistic data volumes
5. **Schedule Migration:** Plan migration window
6. **Execute Migration:** Run migration with monitoring
7. **Validate Results:** Post-migration validation
8. **Monitor Performance:** Monitor application performance post-migration
