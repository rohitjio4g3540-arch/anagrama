"""
Memory storage with adapter abstraction.

This module provides access to memory storage through the storage interface,
allowing seamless switching between JSON and PostgreSQL backends.
"""

from backend.storage.factory import StorageFactory
from backend.storage.interface import MemoryStorageInterface

# Create storage instance based on configuration
memory: MemoryStorageInterface = StorageFactory.create_memory_storage()
