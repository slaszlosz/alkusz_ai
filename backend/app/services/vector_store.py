import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from app.core.config import get_settings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

settings = get_settings()


class VectorStore:
    """Manage vector storage with ChromaDB"""

    def __init__(self):
        self.settings = get_settings()
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=self.settings.openai_api_key,
            model="text-embedding-3-large"  # Best quality embedding model (3072 dimensions)
        )

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.settings.chroma_persist_directory
        )

        # Get or create collection
        self.collection_name = "documents"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_document_chunks(
        self,
        doc_id: str,
        filename: str,
        chunks: List[Dict],
        category: Optional[str] = None
    ) -> int:
        """
        Add document chunks to vector store
        Returns: number of chunks added
        """
        texts = []
        metadatas = []
        ids = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            ids.append(chunk_id)
            texts.append(chunk["text"])

            metadata = {
                "doc_id": doc_id,
                "filename": filename,
                "page": chunk["page"],
                "chunk_index": chunk["chunk_index"]
            }

            if category:
                metadata["category"] = category

            metadatas.append(metadata)

        # Add to collection
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

        return len(texts)

    def search(
        self,
        query: str,
        n_results: int = 5,
        category: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for relevant chunks
        Returns list of results with text, metadata, and score
        """
        where_filter = None
        if category:
            where_filter = {"category": category}

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter
        )

        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "score": 1 - results['distances'][0][i] if results['distances'] else 0
                })

        return formatted_results

    def delete_document(self, doc_id: str):
        """Delete all chunks for a document"""
        self.collection.delete(
            where={"doc_id": doc_id}
        )

    def get_stats(self) -> Dict:
        """Get vector store statistics"""
        count = self.collection.count()
        return {
            "total_chunks": count,
            "collection_name": self.collection_name
        }
