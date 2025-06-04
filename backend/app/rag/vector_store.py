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
        
    def get_documents_by_metadata(self, metadata_filter: Dict[str, Any], include: List[str] = ["documents", "metadatas"]) -> Dict[str, Any]:
        """Get documents from the collection based on metadata filters.
        
        Args:
            metadata_filter (Dict[str, Any]): The filter conditions for metadata.
            include (List[str]): List of data types to include in the response (e.g., "documents", "metadatas").
            
        Returns:
            Dict[str, Any]: Documents and metadata matching the filter.
        """
        try:
            results = self.collection.get(
                where=metadata_filter,
                include=include,
            )
            return results
        except Exception as e:
            print(f"Error getting documents by metadata: {e}")
            raise e

    def get_all_documents(self) -> Dict[str, Any]:
        """Get all documents from the collection.
        
        Returns:
            Dict[str, Any]: All documents with their metadata
        """
        try:
            # Get the total count of documents
            count = self.collection.count()
            
            # Fetch all documents
            results = self.collection.get(
                include=["documents", "metadatas"],
                limit=count
            )
            
            return results
        except Exception as e:
            print(f"Error getting all documents: {e}")
            raise e 