-- Anagrama PostgreSQL Schema
-- Phase 1B: Persistent Data Foundation
-- Core tables for canonical data, derived data, and relationships

-- Enable pgvector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- CORE TABLES (Canonical Data)
-- ============================================================================

-- Users table (single-user first, future multi-user compatible)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Sources table (original/canonical data)
CREATE TABLE IF NOT EXISTS sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    legacy_id TEXT UNIQUE,  -- Preserve original JSON ID
    project_id UUID REFERENCES projects(id),
    title VARCHAR(1000) NOT NULL,
    kind VARCHAR(100) NOT NULL,
    content TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Source files table (for uploaded files)
CREATE TABLE IF NOT EXISTS source_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id),
    filename VARCHAR(500) NOT NULL,
    storage_path VARCHAR(1000) NOT NULL,
    mime_type VARCHAR(100),
    size_bytes BIGINT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Memories table (canonical user data)
CREATE TABLE IF NOT EXISTS memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    legacy_id TEXT UNIQUE,  -- Preserve original JSON ID
    user_id UUID NOT NULL REFERENCES users(id),
    project_id UUID REFERENCES projects(id),
    tier VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    importance_score FLOAT DEFAULT 0.5,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Decisions table (canonical user decisions)
CREATE TABLE IF NOT EXISTS decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    project_id UUID REFERENCES projects(id),
    content TEXT NOT NULL,
    context TEXT,
    alternatives JSONB DEFAULT '[]',
    chosen_alternative UUID,
    rationale TEXT,
    impact TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Tasks table (canonical user tasks)
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    project_id UUID REFERENCES projects(id),
    contract TEXT NOT NULL,
    scope JSONB DEFAULT '{}',
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    progress FLOAT DEFAULT 0.0,
    result JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Skills table (canonical skill definitions)
CREATE TABLE IF NOT EXISTS skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(500) NOT NULL,
    description TEXT,
    procedure JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- ============================================================================
-- KNOWLEDGE GRAPH TABLES
-- ============================================================================

-- Knowledge nodes table (can be canonical or derived)
CREATE TABLE IF NOT EXISTS knowledge_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    legacy_id TEXT UNIQUE,  -- Preserve original JSON ID
    label VARCHAR(500) NOT NULL,
    node_type VARCHAR(100) NOT NULL,
    confidence FLOAT DEFAULT 0.7,
    metadata JSONB DEFAULT '{}',
    is_derived BOOLEAN DEFAULT FALSE,  -- Canonical vs derived flag
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Knowledge edges table (relationships between nodes)
CREATE TABLE IF NOT EXISTS knowledge_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    legacy_id TEXT UNIQUE,  -- Preserve original JSON ID
    source_node_id UUID NOT NULL REFERENCES knowledge_nodes(id),
    target_node_id UUID NOT NULL REFERENCES knowledge_nodes(id),
    relation VARCHAR(100) NOT NULL,
    confidence FLOAT DEFAULT 0.65,
    metadata JSONB DEFAULT '{}',
    is_derived BOOLEAN DEFAULT FALSE,  -- Canonical vs derived flag
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- ============================================================================
-- DERIVED DATA TABLES
-- ============================================================================

-- Embeddings table (derived vector data)
CREATE TABLE IF NOT EXISTS embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    vector VECTOR(1536) NOT NULL,
    model_used VARCHAR(100) NOT NULL,
    model_version VARCHAR(50),
    generated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    confidence FLOAT,
    deleted_at TIMESTAMP
);

-- Summaries table (derived AI summaries)
CREATE TABLE IF NOT EXISTS summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id),
    summary_content TEXT NOT NULL,
    summary_type VARCHAR(50) NOT NULL,
    model_used VARCHAR(100) NOT NULL,
    model_version VARCHAR(50),
    generated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    confidence FLOAT,
    deleted_at TIMESTAMP
);

-- ============================================================================
-- PROVENANCE TABLES
-- ============================================================================

-- Provenance records table (minimal provenance support)
CREATE TABLE IF NOT EXISTS provenance_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    derived_record_id UUID NOT NULL,
    derived_record_type VARCHAR(50) NOT NULL,
    origin_record_id UUID NOT NULL,
    origin_record_type VARCHAR(50) NOT NULL,
    generation_method VARCHAR(100) NOT NULL,
    model_used VARCHAR(100),
    model_version VARCHAR(50),
    parameters JSONB DEFAULT '{}',
    generated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    confidence FLOAT
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Users indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_deleted_at ON users(deleted_at);

-- Projects indexes
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_deleted_at ON projects(deleted_at);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at);

-- Sources indexes
CREATE INDEX IF NOT EXISTS idx_sources_project_id ON sources(project_id);
CREATE INDEX IF NOT EXISTS idx_sources_kind ON sources(kind);
CREATE INDEX IF NOT EXISTS idx_sources_created_at ON sources(created_at);
CREATE INDEX IF NOT EXISTS idx_sources_deleted_at ON sources(deleted_at);
CREATE INDEX IF NOT EXISTS idx_sources_legacy_id ON sources(legacy_id);
CREATE INDEX IF NOT EXISTS idx_sources_metadata ON sources USING GIN(metadata);

-- Source files indexes
CREATE INDEX IF NOT EXISTS idx_source_files_source_id ON source_files(source_id);
CREATE INDEX IF NOT EXISTS idx_source_files_storage_path ON source_files(storage_path);

-- Memories indexes
CREATE INDEX IF NOT EXISTS idx_memories_user_id ON memories(user_id);
CREATE INDEX IF NOT EXISTS idx_memories_project_id ON memories(project_id);
CREATE INDEX IF NOT EXISTS idx_memories_tier ON memories(tier);
CREATE INDEX IF NOT EXISTS idx_memories_importance_score ON memories(importance_score);
CREATE INDEX IF NOT EXISTS idx_memories_created_at ON memories(created_at);
CREATE INDEX IF NOT EXISTS idx_memories_deleted_at ON memories(deleted_at);
CREATE INDEX IF NOT EXISTS idx_memories_legacy_id ON memories(legacy_id);
CREATE INDEX IF NOT EXISTS idx_memories_retrieval ON memories(project_id, importance_score, created_at DESC);

-- Decisions indexes
CREATE INDEX IF NOT EXISTS idx_decisions_user_id ON decisions(user_id);
CREATE INDEX IF NOT EXISTS idx_decisions_project_id ON decisions(project_id);
CREATE INDEX IF NOT EXISTS idx_decisions_created_at ON decisions(created_at);
CREATE INDEX IF NOT EXISTS idx_decisions_deleted_at ON decisions(deleted_at);

-- Tasks indexes
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_tasks_deleted_at ON tasks(deleted_at);

-- Skills indexes
CREATE INDEX IF NOT EXISTS idx_skills_name ON skills(name);
CREATE INDEX IF NOT EXISTS idx_skills_deleted_at ON skills(deleted_at);
CREATE INDEX IF NOT EXISTS idx_skills_procedure ON skills USING GIN(procedure);

-- Knowledge nodes indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_nodes_node_type ON knowledge_nodes(node_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_nodes_label ON knowledge_nodes(label);
CREATE INDEX IF NOT EXISTS idx_knowledge_nodes_confidence ON knowledge_nodes(confidence);
CREATE INDEX IF NOT EXISTS idx_knowledge_nodes_created_at ON knowledge_nodes(created_at);
CREATE INDEX IF NOT EXISTS idx_knowledge_nodes_deleted_at ON knowledge_nodes(deleted_at);
CREATE INDEX IF NOT EXISTS idx_knowledge_nodes_is_derived ON knowledge_nodes(is_derived);
CREATE INDEX IF NOT EXISTS idx_knowledge_nodes_legacy_id ON knowledge_nodes(legacy_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_nodes_metadata ON knowledge_nodes USING GIN(metadata);

-- Knowledge edges indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_edges_source_node_id ON knowledge_edges(source_node_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_edges_target_node_id ON knowledge_edges(target_node_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_edges_relation ON knowledge_edges(relation);
CREATE INDEX IF NOT EXISTS idx_knowledge_edges_confidence ON knowledge_edges(confidence);
CREATE INDEX IF NOT EXISTS idx_knowledge_edges_created_at ON knowledge_edges(created_at);
CREATE INDEX IF NOT EXISTS idx_knowledge_edges_deleted_at ON knowledge_edges(deleted_at);
CREATE INDEX IF NOT EXISTS idx_knowledge_edges_is_derived ON knowledge_edges(is_derived);
CREATE INDEX IF NOT EXISTS idx_knowledge_edges_legacy_id ON knowledge_edges(legacy_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_edges_metadata ON knowledge_edges USING GIN(metadata);

-- Embeddings indexes
CREATE INDEX IF NOT EXISTS idx_embeddings_entity_id ON embeddings(entity_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_entity_type ON embeddings(entity_type);
CREATE INDEX IF NOT EXISTS idx_embeddings_deleted_at ON embeddings(deleted_at);
CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON embeddings USING hnsw(vector vector_cosine_ops);

-- Summaries indexes
CREATE INDEX IF NOT EXISTS idx_summaries_source_id ON summaries(source_id);
CREATE INDEX IF NOT EXISTS idx_summaries_summary_type ON summaries(summary_type);
CREATE INDEX IF NOT EXISTS idx_summaries_deleted_at ON summaries(deleted_at);

-- Provenance records indexes
CREATE INDEX IF NOT EXISTS idx_provenance_records_derived_record_id ON provenance_records(derived_record_id);
CREATE INDEX IF NOT EXISTS idx_provenance_records_derived_record_type ON provenance_records(derived_record_type);
CREATE INDEX IF NOT EXISTS idx_provenance_records_origin_record_id ON provenance_records(origin_record_id);
CREATE INDEX IF NOT EXISTS idx_provenance_records_origin_record_type ON provenance_records(origin_record_type);
CREATE INDEX IF NOT EXISTS idx_provenance_records_generated_at ON provenance_records(generated_at);

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to tables that need it
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_memories_updated_at BEFORE UPDATE ON memories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_nodes_updated_at BEFORE UPDATE ON knowledge_nodes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_edges_updated_at BEFORE UPDATE ON knowledge_edges
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_skills_updated_at BEFORE UPDATE ON skills
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
