# Anagrama Infrastructure Requirements

> Analysis of minimum infrastructure needed to run, test, and deploy Anagrama as of 2026-09-12

## Current State Summary

**Phase Status:**
- ✅ Phase 0: Architecture Stabilization - COMPLETE
- ✅ Phase 1A: Schema Design & Migration Strategy - COMPLETE
- ✅ Phase 1B Step 1: Storage Foundation Validation - COMPLETE
- ⏸️ Phase 1B Step 2A: PostgreSQL Environment Setup - BLOCKED (infrastructure unavailable)

**Active Backend:** JSON file-based storage
**Ready Backend:** PostgreSQL (adapter implemented, not activated)

---

## 1. MINIMUM INFRASTRUCTURE FOR CURRENT DEVELOPMENT

### Required for Local Development (JSON Backend - Working Today)

**Runtime:**
- Python 3.12+ (tested with 3.14.4)
- Node.js 20+ (for Next.js 16.2.10)

**Python Dependencies** (from requirements.txt):
```
fastapi>=0.115.0
pydantic>=2.8.0
python-dotenv>=1.0.1
python-multipart>=0.0.9
google-genai>=1.0.0
psycopg2-binary>=2.9.0
alembic>=1.13.0
pytest>=8.0.0
openai>=1.0.0
uvicorn>=0.30.0
```

**Node.js Dependencies** (from package.json):
```json
{
  "dependencies": {
    "framer-motion": "^12.42.2",
    "next": "16.2.10",
    "react": "19.2.4",
    "react-dom": "19.2.4"
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4",
    "@types/node": "^20",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "eslint": "^9",
    "eslint-config-next": "16.2.10",
    "tailwindcss": "^4",
    "typescript": "^5"
  }
}
```

**External Services:**
- Google Gemini API (GEMINI_API_KEY required for LLM functionality)

**Environment Variables** (from .env.example):
```bash
GEMINI_API_KEY=                    # REQUIRED for LLM features
GEMINI_MODEL=gemini-2.5-flash       # Optional, has default
GEMINI_FALLBACK_MODEL=gemini-3.5-flash  # Optional, has default
DATABASE_URL=sqlite:///./storage/anagrama.db  # Optional, unused currently
POSTGRES_URL=postgresql://...      # Optional, for PostgreSQL backend
USE_POSTGRES=false                 # Default: use JSON
ANAGRAMA_STORAGE_PATH=storage/uploads
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Storage (JSON Backend - No Database Required):**
- `storage/anagrama-state.json` - Graph data
- `storage/memory.json` - Memory data
- `storage/uploads/` - File uploads

**Startup Commands:**
```bash
# Backend
npm run api:dev        # Python: uvicorn backend.main:app --reload --port 8000

# Frontend
npm run dev            # Next.js dev server

# Tests
npm run api:test        # Python: pytest backend/tests -q
```

**Summary:** Current development works with Python + Node.js + Gemini API key. No database required.

---

## 2. TESTING INFRASTRUCTURE

### Current Test Status

**Test Suite:** 33 passed, 3 skipped (as of Phase 1B Step 1)

**Test Categories:**
- Agent tests: 4 passed
- API tests: 1 passed, 1 skipped (stream test requires API key)
- Pipeline tests: 2 passed
- Storage adapter tests: 26 passed, 2 skipped (PostgreSQL integration tests)

**PostgreSQL Integration Tests:**
- Skipped unless POSTGRES_URL is configured
- Currently only placeholder assertions (would need real database for full validation)
- Located in `backend/tests/test_storage_adapters.py` (lines 482-512)

**Testing Requirements:**
- pytest (included in requirements.txt)
- JSON backend: Tests pass with no additional infrastructure
- PostgreSQL backend: Requires PostgreSQL instance with pgvector

---

## 3. PHASE 1B STEP 2A: POSTGRESQL VALIDATION

### Why PostgreSQL is Required

The task explicitly requires:
1. Set up a development PostgreSQL environment
2. Enable pgvector extension
3. Apply schema.sql (contains PostgreSQL-specific syntax)
4. Connect PostgreSQL adapter
5. Test with isolated test data

### PostgreSQL-Specific Requirements

**Database Version:** PostgreSQL 16+ (for pgvector compatibility)

**Extensions Required:**
- pgvector (for vector similarity search in future phases)

**Schema Requirements:**
- UUID data types
- JSONB data type
- GIN indexes (for JSONB)
- pgvector vector type
- PostgreSQL-specific triggers and functions

**Connection:** psycopg2 adapter requires real PostgreSQL connection

### Infrastructure Options

**Option A: Docker (Recommended for Development)**
```yaml
# Already defined in docker-compose.yml
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: anagrama
      POSTGRES_USER: anagrama
      POSTGRES_PASSWORD: anagrama
    ports: ["5432:5432"]
```

**Requirements:**
- Docker Desktop or Docker Engine
- Docker Compose
- 5432 port available

**Option B: Local PostgreSQL Installation**
- PostgreSQL 16+ installed locally
- pgvector extension installed
- Database and user created manually

**Option C: Cloud PostgreSQL**
- Cloud PostgreSQL instance (e.g., Supabase, Neon, AWS RDS)
- pgvector extension available
- Network access from development machine

### Current Blocker

**Status:** BLOCKED
**Reason:** Docker not available in current Windows environment
**Impact:** Cannot validate PostgreSQL adapter or proceed with Phase 1B Step 2A

---

## 4. DEPLOYMENT INFRASTRUCTURE

### Vercel Configuration (Already Defined)

**File:** `vercel.json`

**Services:**
- Frontend: Next.js (apps/web/)
- Backend: FastAPI (backend/)

**Rewrites:**
- `/api/*` → Backend service
- `/*` → Frontend service

### Deployment Requirements

**Vercel-Specific:**
- Environment variables configured in Vercel dashboard
- Build commands: `npm run build` (frontend), automatic for FastAPI
- Start commands: automatic for both services

**For PostgreSQL Backend Deployment:**
- Vercel Postgres add-on OR external PostgreSQL
- POSTGRES_URL environment variable
- USE_POSTGRES=true
- pgvector extension available

**For JSON Backend Deployment (Current):**
- No database required
- Storage: Vercel's ephemeral filesystem (/tmp)
- ⚠️ Note: JSON storage on Vercel is ephemeral (not persistent across deployments)

---

## 5. SCALING INFRASTRUCTURE NEEDS

### By Phase

**Phase 0 (Current):**
- ✅ Python + Node.js + Gemini API key
- ✅ JSON storage (working)

**Phase 1B Step 2A (Blocked):**
- ❌ PostgreSQL 16 + pgvector
- ❌ Docker OR local PostgreSQL OR cloud PostgreSQL

**Phase 1B Step 2B (Future - Migration):**
- PostgreSQL 16 + pgvector
- Migration scripts execution
- Data validation tools
- Rollback procedures

**Phase 2 (Future - Hybrid Retrieval):**
- PostgreSQL 16 + pgvector
- Embedding service (OpenAI, Cohere, or local)
- Vector index tuning

**Phase 3+ (Future):**
- Potential Neo4j (optional, for advanced graph queries)
- Redis (for caching)
- Object storage (S3 equivalent for file uploads)

---

## 6. MINIMUM VIABLE INFRASTRUCTURE SUMMARY

### To Continue Current Development (JSON Backend)

**Required:**
- ✅ Python 3.12+
- ✅ Node.js 20+
- ✅ Google Gemini API key

**Optional:**
- PostgreSQL (not needed for current JSON backend)
- Docker (not needed for current JSON backend)

**Status:** WORKING NOW

### To Complete Phase 1B Step 2A (PostgreSQL Validation)

**Required:**
- ❌ PostgreSQL 16 with pgvector extension
- ❌ One of:
  - Docker Desktop + docker-compose
  - Local PostgreSQL 16 installation
  - Cloud PostgreSQL instance with pgvector

**Status:** BLOCKED

### To Deploy to Production

**Minimum (JSON Backend):**
- Vercel account
- Google Gemini API key
- ⚠️ Accept ephemeral storage limitation

**Recommended (PostgreSQL Backend):**
- Vercel account
- Vercel Postgres add-on OR external PostgreSQL with pgvector
- Google Gemini API key
- Persistent storage

---

## 7. INFRASTRUCTURE RECOMMENDATIONS

### Immediate (To Unblock Phase 1B Step 2A)

**Option 1: Install Docker Desktop** (Recommended)
- Download Docker Desktop for Windows
- Run `docker compose up -d postgres` from project root
- Configure POSTGRES_URL in .env
- Proceed with Phase 1B Step 2A

**Option 2: Install PostgreSQL Locally**
- Install PostgreSQL 16 for Windows
- Install pgvector extension
- Create database and user
- Configure POSTGRES_URL in .env
- Proceed with Phase 1B Step 2A

**Option 3: Use Cloud PostgreSQL**
- Create Supabase/Neon account (free tier available)
- Enable pgvector extension
- Configure POSTGRES_URL in .env
- Proceed with Phase 1B Step 2A

### For Production Deployment

**Recommended Stack:**
- Vercel for hosting (Next.js + FastAPI)
- Vercel Postgres for database (includes pgvector)
- Google Gemini API for LLM
- Vercel environment variables for configuration

---

## 8. COST ESTIMATES

### Development (Local)
- Docker Desktop: Free
- PostgreSQL: Free (local)
- Gemini API: Pay-per-use (free tier available)
- **Total: $0 (excluding API usage)**

### Production (Vercel + Vercel Postgres)
- Vercel Hobby: Free (limited)
- Vercel Postgres: $20/month (Hobby plan)
- Gemini API: Pay-per-use
- **Total: ~$20/month + API usage**

### Alternative (Supabase + Vercel)
- Vercel: Free
- Supabase Free Tier: Free (500MB database)
- Gemini API: Pay-per-use
- **Total: $0 + API usage** (with limits)

---

## 9. SECURITY CONSIDERATIONS

**Environment Variables to Protect:**
- GEMINI_API_KEY - Secret
- POSTGRES_URL - Secret (contains credentials)
- NEO4J_PASSWORD - Secret (if using Neo4j)

**Never Commit:**
- .env file
- Any actual API keys or passwords

**Recommended:**
- Use .env.example as template
- Use Vercel environment variables for deployment
- Use secret management service for production

---

## 10. DECISION REQUIRED

### Current Blocker

**Phase 1B Step 2A cannot proceed without PostgreSQL infrastructure.**

**Choose one:**
1. Install Docker Desktop and use docker-compose.yml
2. Install PostgreSQL 16 locally with pgvector
3. Use cloud PostgreSQL (Supabase, Neon, etc.)
4. Defer Phase 1B Step 2A until infrastructure available
5. Alternative: Authorize mock-based testing approach (would not validate real PostgreSQL code)

**Recommendation:** Option 1 (Docker) is simplest for development and matches existing docker-compose.yml configuration.
