"""
Storage package for Anagrama.

This package provides storage abstraction with multiple backend implementations:
- Interface definitions for storage operations
- JSON adapter for development
- PostgreSQL adapter for production
- Factory for backend selection based on configuration
"""

from backend.storage.interface import GraphStorageInterface, MemoryStorageInterface
from backend.storage.factory import StorageFactory

__all__ = [
    'GraphStorageInterface',
    'MemoryStorageInterface', 
    'StorageFactory'
]
