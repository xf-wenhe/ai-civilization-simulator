"""
Memory system using ChromaDB for semantic search over agent memories.
Provides long-term memory storage and retrieval.
"""

from typing import List, Dict, Optional
import chromadb
from datetime import datetime
import json


class AgentMemorySystem:
    """Semantic memory system for agents using vector embeddings"""

    def __init__(self, persist_directory: str = "./data/chroma"):
        """Initialize ChromaDB client with new API"""
        # 使用新的ChromaDB API
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Create collections for different memory types
        self.episodic_collection = self.client.get_or_create_collection("episodic_memories")
        self.semantic_collection = self.client.get_or_create_collection("semantic_memories")
        self.procedural_collection = self.client.get_or_create_collection("procedural_memories")

    def store_memory(self, agent_id: str, memory_type: str, content: str,
                    timestamp: int, importance: float, metadata: Dict = None):

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

        results.sort(key=lambda x: x['metadata'].get('importance', 0), reverse=True)
        return results[:n_results]

    def get_recent_memories(self, agent_id: str, memory_type: str = None,
                           limit: int = 20) -> List[Dict]:

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

        results.sort(key=lambda x: x['metadata'].get('timestamp', 0), reverse=True)
        return results[:limit]

    def _get_collection(self, memory_type: str):
        if memory_type == "episodic":
            return self.episodic_collection
        elif memory_type == "semantic":
            return self.semantic_collection
        elif memory_type == "procedural":
            return self.procedural_collection
        return None

    def export_agent_memories(self, agent_id: str) -> Dict:
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