"""
Knowledge graph storage with adapter abstraction.

This module provides access to graph storage through the storage interface,
allowing seamless switching between JSON and PostgreSQL backends.
"""

from backend.storage.factory import StorageFactory
from backend.storage.interface import GraphStorageInterface

# Create storage instance based on configuration
graph: GraphStorageInterface = StorageFactory.create_graph_storage()
