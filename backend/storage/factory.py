"""
Storage factory for creating storage instances.

This factory provides a single point for creating storage instances based on
configuration, ensuring consistent storage backend selection across the application.
"""

from backend.storage.interface import GraphStorageInterface, MemoryStorageInterface
from backend.storage.json_adapter import JSONGraphStorage, JSONMemoryStorage
from backend.storage.postgres_adapter import PostgresGraphStorage, PostgresMemoryStorage
from backend.config.settings import get_settings


class StorageFactory:
    """Factory for creating storage instances based on configuration."""
    
    @staticmethod
    def create_graph_storage() -> GraphStorageInterface:
        """Create a graph storage instance based on configuration."""
        settings = get_settings()
        
        if settings.use_postgres and settings.postgres_url:
            return PostgresGraphStorage()
        else:
            return JSONGraphStorage()
    
    @staticmethod
    def create_memory_storage() -> MemoryStorageInterface:
        """Create a memory storage instance based on configuration."""
        settings = get_settings()
        
        if settings.use_postgres and settings.postgres_url:
            return PostgresMemoryStorage()
        else:
            return JSONMemoryStorage()
