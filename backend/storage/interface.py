"""
Storage interface abstraction for Anagrama.

This provides a common interface that can be implemented by different storage backends
(JSON for development, PostgreSQL for production), allowing seamless switching without
breaking existing application code.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from backend.models.schemas import Source, GraphNode, GraphEdge, Memory


class GraphStorageInterface(ABC):
    """Interface for knowledge graph storage operations."""
    
    @abstractmethod
    def add_source(self, source: Source, user_id: str) -> None:
        """Add a source to storage."""
        pass
    
    @abstractmethod
    def upsert_node(self, node: GraphNode, user_id: str) -> None:
        """Add or update a node in storage."""
        pass
    
    @abstractmethod
    def add_edge(self, edge: GraphEdge, user_id: str) -> None:
        """Add an edge to storage."""
        pass
    
    @abstractmethod
    def snapshot(self, user_id: str) -> Dict[str, Any]:
        """Get a snapshot of the graph (nodes, edges, sources)."""
        pass
    
    @abstractmethod
    def projects(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all projects."""
        pass
    
    @abstractmethod
    def add_project(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Add a project to storage."""
        pass


class MemoryStorageInterface(ABC):
    """Interface for memory storage operations."""
    
    @abstractmethod
    def all(self, project_id: Optional[str] = None, user_id: Optional[str] = None) -> List[Memory]:
        """Get all memories, optionally filtered by project_id."""
        pass
    
    @abstractmethod
    def add(self, tier: str, content: str, project_id: Optional[str] = None, user_id: Optional[str] = None) -> Memory:
        """Add a memory to storage."""
        pass


class StorageFactory:
    """Factory for creating storage instances based on configuration."""
    

