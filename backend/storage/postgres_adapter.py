from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.schemas import Source, GraphNode, GraphEdge, Memory
from backend.storage.interface import GraphStorageInterface, MemoryStorageInterface
from backend.storage.db import (
    SessionLocal, 
    Project as ProjectModel, 
    MemoryModel, 
    SourceModel, 
    KnowledgeNode, 
    KnowledgeEdge,
    User
)
from backend.utils.ids import new_id

class PostgresGraphStorage(GraphStorageInterface):
    
    def _get_session(self):
        return SessionLocal()
        
    def add_source(self, source: Source, user_id: str) -> None:
        db = self._get_session()
        try:
            db_source = SourceModel(
                id=source.id,
                legacy_id=source.id,
                user_id=user_id,
                title=source.title,
                kind=source.kind,
                content=source.content,
                metadata_=source.metadata,
                created_at=source.created_at if not isinstance(source.created_at, str) else datetime.fromisoformat(source.created_at.replace('Z', '+00:00'))
            )
            db.merge(db_source)
            db.commit()
        finally:
            db.close()
            
    def upsert_node(self, node: GraphNode, user_id: str) -> None:
        db = self._get_session()
        try:
            db_node = db.query(KnowledgeNode).filter(KnowledgeNode.id == node.id, KnowledgeNode.user_id == user_id).first()
            if db_node:
                existing_source_ids = db_node.metadata_.get("source_ids", []) if db_node.metadata_ else []
                updated_source_ids = sorted(set(existing_source_ids + node.source_ids))
                db_node.metadata_ = {"source_ids": updated_source_ids}
                db_node.confidence = max(db_node.confidence, node.confidence)
                db_node.updated_at = datetime.utcnow()
            else:
                db_node = KnowledgeNode(
                    id=node.id,
                    legacy_id=node.id,
                    user_id=user_id,
                    label=node.label,
                    node_type=node.type,
                    confidence=node.confidence,
                    metadata_={"source_ids": node.source_ids},
                    is_derived=False
                )
                db.add(db_node)
            db.commit()
        finally:
            db.close()
            
    def add_edge(self, edge: GraphEdge, user_id: str) -> None:
        db = self._get_session()
        try:
            existing = db.query(KnowledgeEdge).filter(
                KnowledgeEdge.source_node_id == edge.source,
                KnowledgeEdge.target_node_id == edge.target,
                KnowledgeEdge.relation == edge.relation,
                KnowledgeEdge.user_id == user_id
            ).first()
            if not existing:
                db_edge = KnowledgeEdge(
                    id=edge.id,
                    legacy_id=edge.id,
                    user_id=user_id,
                    source_node_id=edge.source,
                    target_node_id=edge.target,
                    relation=edge.relation,
                    confidence=edge.confidence,
                    metadata_={"evidence": edge.evidence},
                    is_derived=False
                )
                db.add(db_edge)
                db.commit()
        finally:
            db.close()

    def snapshot(self, user_id: str) -> Dict[str, Any]:
        db = self._get_session()
        try:
            nodes = []
            for n in db.query(KnowledgeNode).filter(KnowledgeNode.deleted_at == None, KnowledgeNode.user_id == user_id).all():
                nodes.append({
                    "id": n.id,
                    "label": n.label,
                    "type": n.node_type,
                    "confidence": n.confidence,
                    "source_ids": n.metadata_.get("source_ids", []) if n.metadata_ else []
                })
            
            edges = []
            for e in db.query(KnowledgeEdge).filter(KnowledgeEdge.deleted_at == None, KnowledgeEdge.user_id == user_id).all():
                edges.append({
                    "id": e.id,
                    "source": e.source_node_id,
                    "target": e.target_node_id,
                    "relation": e.relation,
                    "confidence": e.confidence,
                    "evidence": e.metadata_.get("evidence", []) if e.metadata_ else []
                })
                
            sources = []
            for s in db.query(SourceModel).filter(SourceModel.deleted_at == None, SourceModel.user_id == user_id).all():
                sources.append({
                    "id": s.id,
                    "title": s.title,
                    "kind": s.kind,
                    "content": s.content,
                    "metadata": s.metadata_ or {},
                    "created_at": s.created_at.isoformat() if s.created_at else None
                })
                
            return {"nodes": nodes, "edges": edges, "sources": sources}
        finally:
            db.close()

    def projects(self, user_id: str) -> List[Dict[str, Any]]:
        db = self._get_session()
        try:
            projects = []
            for p in db.query(ProjectModel).filter(ProjectModel.deleted_at == None, ProjectModel.user_id == user_id).all():
                projects.append({
                    "id": p.id,
                    "title": p.title,
                    "description": p.description or ""
                })
            return projects
        finally:
            db.close()

    def add_project(self, project: Dict[str, Any]) -> Dict[str, Any]:
        db = self._get_session()
        try:
            proj_id = new_id("proj")
            new_proj = ProjectModel(
                id=proj_id,
                user_id=project["user_id"],
                title=project["title"],
                description=project.get("description", "")
            )
            db.add(new_proj)
            db.commit()
            
            project["id"] = proj_id
            return project
        finally:
            db.close()

class PostgresMemoryStorage(MemoryStorageInterface):
    
    def _get_session(self):
        return SessionLocal()
        
    def all(self, project_id: Optional[str] = None, user_id: Optional[str] = None) -> List[Memory]:
        db = self._get_session()
        try:
            query = db.query(MemoryModel).filter(MemoryModel.deleted_at == None)
            if project_id:
                query = query.filter(MemoryModel.project_id == project_id)
            if user_id:
                query = query.filter(MemoryModel.user_id == user_id)
            
            memories = []
            for m in query.all():
                memories.append(Memory(
                    id=m.id,
                    tier=m.tier,
                    content=m.content,
                    project_id=m.project_id,
                    created_at=m.created_at
                ))
            return memories
        finally:
            db.close()

    def add(self, tier: str, content: str, project_id: Optional[str] = None, user_id: Optional[str] = None) -> Memory:
        db = self._get_session()
        try:
            mem_id = new_id("mem")
            new_mem = MemoryModel(
                id=mem_id,
                legacy_id=mem_id,
                user_id=user_id,
                tier=tier,
                content=content,
                project_id=project_id
            )
            db.add(new_mem)
            db.commit()
            
            return Memory(
                id=mem_id,
                tier=tier,
                content=content,
                project_id=project_id,
                created_at=datetime.utcnow()
            )
        finally:
            db.close()

