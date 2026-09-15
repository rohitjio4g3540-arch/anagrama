import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Float, Boolean
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine
from backend.config.settings import get_settings

Base = declarative_base()
settings = get_settings()

if settings.use_postgres and settings.active_database_url.startswith("postgresql"):
    from pgvector.sqlalchemy import Vector
    VectorType = Vector(1536)
else:
    VectorType = JSON # Fallback for local sqlite tests


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    projects = relationship("Project", back_populates="user")
    memories = relationship("MemoryModel", back_populates="user")

class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    title = Column(String)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="projects")
    memories = relationship("MemoryModel", back_populates="project")

class MemoryModel(Base):
    __tablename__ = "memories"
    id = Column(String, primary_key=True, index=True)
    legacy_id = Column(String, nullable=True)
    user_id = Column(String, ForeignKey("users.id"))
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    tier = Column(String)
    content = Column(Text)
    embedding = Column(VectorType, nullable=True) # Adjust dim if needed
    created_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="memories")
    project = relationship("Project", back_populates="memories")

class SourceModel(Base):
    __tablename__ = "sources"
    id = Column(String, primary_key=True, index=True)
    legacy_id = Column(String, nullable=True)
    user_id = Column(String, ForeignKey("users.id"))
    title = Column(String)
    kind = Column(String)
    content = Column(Text)
    metadata_ = Column("metadata", JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    user = relationship("User")

class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"
    id = Column(String, primary_key=True, index=True)
    legacy_id = Column(String, nullable=True)
    user_id = Column(String, ForeignKey("users.id"))
    label = Column(String)
    node_type = Column(String)
    confidence = Column(Float)
    metadata_ = Column("metadata", JSON)
    is_derived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    user = relationship("User")

class KnowledgeEdge(Base):
    __tablename__ = "knowledge_edges"
    id = Column(String, primary_key=True, index=True)
    legacy_id = Column(String, nullable=True)
    user_id = Column(String, ForeignKey("users.id"))
    source_node_id = Column(String, ForeignKey("knowledge_nodes.id"))
    target_node_id = Column(String, ForeignKey("knowledge_nodes.id"))
    relation = Column(String)
    confidence = Column(Float)
    metadata_ = Column("metadata", JSON)
    is_derived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    user = relationship("User")

settings = get_settings()
engine = create_engine(settings.active_database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
