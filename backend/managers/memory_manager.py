import os
import chromadb

class MemoryManager:
    def __init__(self, db_path="./chroma_db"):
        # We use a persistent client so memories survive restarts
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name="long_term_memory")
        
    def add_memory(self, text, role="user"):
        if not text or not text.strip():
            return
        # Use a simple hash for doc_id
        import hashlib
        doc_id = hashlib.md5((text + role).encode('utf-8')).hexdigest()
        
        # Check if it already exists
        existing = self.collection.get(ids=[doc_id])
        if not existing['ids']:
            self.collection.add(
                documents=[text],
                metadatas=[{"role": role}],
                ids=[doc_id]
            )
        
    def get_context(self, query, n_results=5):
        if not query or not query.strip():
            return ""
        if self.collection.count() == 0:
            return ""
            
        # Query the vector database for relevant past memories
        results = self.collection.query(
            query_texts=[query],
            n_results=min(n_results, self.collection.count())
        )
        
        if not results['documents'] or not results['documents'][0]:
            return ""
            
        context_parts = []
        for i, doc in enumerate(results['documents'][0]):
            role = results['metadatas'][0][i]['role']
            context_parts.append(f"[{role.capitalize()}]: {doc}")
            
        return "\n".join(context_parts)
