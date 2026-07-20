from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

class Source(BaseModel):
    id: str
    title: str
    kind: str = "note"
    content: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, str] = Field(default_factory=dict)

class GraphNode(BaseModel):
    id: str
    label: str
    type: Literal["concept", "entity", "person", "organization", "document", "project", "conversation"] = "concept"
    confidence: float = 0.7
    source_ids: list[str] = Field(default_factory=list)

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    relation: str
    confidence: float = 0.65
    evidence: list[str] = Field(default_factory=list)

class Memory(BaseModel):
    id: str
    tier: Literal["working", "conversation", "project", "knowledge", "personal"]
    content: str
    project_id: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=40_000)
    project_id: str | None = None
    conversation_id: str | None = None

class ProjectRequest(BaseModel):
    title: str = Field(min_length=1, max_length=240)
    description: str = ""

class SearchResult(BaseModel):
    source: Source
    score: float
    excerpt: str
