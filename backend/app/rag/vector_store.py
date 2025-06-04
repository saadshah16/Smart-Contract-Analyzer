from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import os

class VectorStoreManager:
    def __init__(
        self,
        persist_directory: str = "chroma_db",
        collection_name: str = "smart_contract_analysis"
    ):
        """Initialize the vector store manager with Chroma.
        
        Args:
            persist_directory (str): Directory to persist the vector store
            collection_name (str): Name of the collection to use
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Use sentence-transformers for embeddings
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Create or get the collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
        where: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add documents to the vector store.
        
        Args:
            documents (List[str]): List of document texts
            metadatas (List[Dict[str, Any]]): List of metadata for each document
            ids (List[str]): List of unique IDs for each document
            where (Optional[Dict[str, Any]]): Filter conditions for the collection
        """
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Search for similar documents.
        
        Args:
            query (str): The search query
            n_results (int): Number of results to return
            where (Optional[Dict[str, Any]]): Filter conditions for the search
            
        Returns:
            Dict[str, Any]: Search results containing documents, metadatas, and distances
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )
        return results
    
    def delete_collection(self) -> None:
        """Delete the current collection."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function
        )
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection.
        
        Returns:
            Dict[str, Any]: Collection statistics
        """
        return {
            "count": self.collection.count(),
            "name": self.collection.name
        } 