"""
Memory system using ChromaDB for semantic search over agent memories.
Provides long-term memory storage and retrieval.
"""

from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from datetime import datetime
import json


class AgentMemorySystem:
    """Semantic memory system for agents using vector embeddings"""

    def __init__(self, persist_directory: str = "./data/chroma"):
        """Initialize ChromaDB client"""
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory
        ))

        # Create collections for different memory types
        self.episodic_collection = self.client.get_or_create_collection("episodic_memories")
        self.semantic_collection = self.client.get_or_create_collection("semantic_memories")
        self.procedural_collection = self.client.get_or_create_collection("procedural_memories")

    def store_memory(self, agent_id: str, memory_type: str, content: str,
                    timestamp: int, importance: float, metadata: Dict = None):
        """Store a memory in the appropriate collection"""

        metadata = metadata or {}
        metadata.update({
            "agent_id": agent_id,
            "timestamp": timestamp,
            "importance": importance,
            "created_at": datetime.now().isoformat()
        })

        memory_id = f"{agent_id}_{timestamp}_{memory_type}"

        collection = self._get_collection(memory_type)
        if collection:
            collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[memory_id]
            )

    def search_memories(self, agent_id: str, query: str, memory_type: str = None,
                       n_results: int = 10) -> List[Dict]:
        """Search memories semantically"""

        if memory_type:
            collections = [self._get_collection(memory_type)]
        else:
            collections = [
                self.episodic_collection,
                self.semantic_collection,
                self.procedural_collection
            ]

        results = []
        for collection in collections:
            if collection:
                search_results = collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    where={"agent_id": agent_id}
                )

                for i, doc in enumerate(search_results['documents'][0]):
                    results.append({
                        "content": doc,
                        "metadata": search_results['metadatas'][0][i],
                        "distance": search_results['distances'][0][i] if 'distances' in search_results else None
                    })

        # Sort by importance
        results.sort(key=lambda x: x['metadata'].get('importance', 0), reverse=True)

        return results[:n_results]

    def get_recent_memories(self, agent_id: str, memory_type: str = None,
                           limit: int = 20) -> List[Dict]:
        """Get recent memories for an agent"""

        if memory_type:
            collections = [self._get_collection(memory_type)]
        else:
            collections = [
                self.episodic_collection,
                self.semantic_collection,
                self.procedural_collection
            ]

        results = []
        for collection in collections:
            if collection:
                collection_results = collection.get(
                    where={"agent_id": agent_id},
                    limit=limit
                )

                for i, doc in enumerate(collection_results['documents']):
                    results.append({
                        "content": doc,
                        "metadata": collection_results['metadatas'][i]
                    })

        # Sort by timestamp
        results.sort(key=lambda x: x['metadata'].get('timestamp', 0), reverse=True)

        return results[:limit]

    def update_memory_importance(self, memory_id: str, new_importance: float):
        """Update importance score for a memory"""

        # Need to retrieve, delete, and re-add
        # This is a limitation of ChromaDB - no direct update
        pass

    def forget_old_memories(self, agent_id: str, keep_last: int = 100):
        """Remove old, unimportant memories"""

        for collection in [self.episodic_collection, self.semantic_collection, self.procedural_collection]:
            all_memories = collection.get(
                where={"agent_id": agent_id}
            )

            if len(all_memories['ids']) > keep_last:
                # Sort by importance and timestamp
                memory_data = [
                    {
                        "id": all_memories['ids'][i],
                        "importance": all_memories['metadatas'][i].get('importance', 0),
                        "timestamp": all_memories['metadatas'][i].get('timestamp', 0)
                    }
                    for i in range(len(all_memories['ids']))
                ]

                memory_data.sort(key=lambda x: (x['importance'], x['timestamp']), reverse=True)

                # Delete memories not in top `keep_last`
                ids_to_delete = [m['id'] for m in memory_data[keep_last:]]
                if ids_to_delete:
                    collection.delete(ids=ids_to_delete)

    def _get_collection(self, memory_type: str):
        """Get collection by memory type"""
        if memory_type == "episodic":
            return self.episodic_collection
        elif memory_type == "semantic":
            return self.semantic_collection
        elif memory_type == "procedural":
            return self.procedural_collection
        return None

    def export_agent_memories(self, agent_id: str) -> Dict:
        """Export all memories for an agent"""
        all_memories = {}

        for mem_type in ["episodic", "semantic", "procedural"]:
            collection = self._get_collection(mem_type)
            if collection:
                results = collection.get(where={"agent_id": agent_id})
                all_memories[mem_type] = [
                    {
                        "content": results['documents'][i],
                        "metadata": results['metadatas'][i]
                    }
                    for i in range(len(results['ids']))
                ]

        return all_memories