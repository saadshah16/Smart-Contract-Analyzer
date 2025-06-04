from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os
import uuid
from .vector_store import VectorStoreManager

class KnowledgeBaseManager:
    def __init__(self, persist_directory: str = "chroma_db"):
        """Initialize the knowledge base manager.
        
        Args:
            persist_directory (str): Directory to persist the vector store
        """
        self.vector_store = VectorStoreManager(
            persist_directory=persist_directory,
            collection_name="smart_contract_knowledge_base"
        )
    
    def add_knowledge_item(
        self,
        content: str,
        category: str,
        pattern_type: str,
        severity: int = 0,
        standard: Optional[str] = None,
        version: Optional[str] = None,
        references: Optional[List[str]] = None,
        code_example: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a knowledge base item.
        
        Args:
            content (str): The main content/description of the knowledge item
            category (str): Category of the knowledge (e.g., "security_pattern", "vulnerability")
            pattern_type (str): Specific pattern type (e.g., "reentrancy", "access_control")
            severity (int): Severity level (1-5) for vulnerabilities
            standard (Optional[str]): Related standard (e.g., "ERC-20", "ERC-721")
            version (Optional[str]): Solidity version
            references (Optional[List[str]]): List of reference links
            code_example (Optional[str]): Example code implementation
            description (Optional[str]): Additional description
            
        Returns:
            Dict[str, Any]: Statistics about the added item
        """
        # Validate severity
        if severity < 0 or severity > 5:
            raise ValueError("Severity must be between 0 and 5")
            
        # Create metadata
        metadata = {
            "category": category,
            "pattern_type": pattern_type,
            "severity": severity,
            "standard": standard,
            "version": version,
            "references": json.dumps(references) if references is not None else None,
            "code_example": code_example,
            "description": description,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # Generate unique ID
        item_id = f"kb_{uuid.uuid4()}"
        
        # Add to vector store
        self.vector_store.add_documents(
            documents=[content],
            metadatas=[metadata],
            ids=[item_id]
        )
        
        return {
            "id": item_id,
            "metadata": metadata
        }
    
    def search_knowledge(
        self,
        query: str,
        category: Optional[str] = None,
        pattern_type: Optional[str] = None,
        min_severity: Optional[int] = None,
        standard: Optional[str] = None,
        n_results: int = 3
    ) -> Dict[str, Any]:
        """Search the knowledge base with filters.
        
        Args:
            query (str): Search query
            category (Optional[str]): Filter by category
            pattern_type (Optional[str]): Filter by pattern type
            min_severity (Optional[int]): Filter by minimum severity
            standard (Optional[str]): Filter by standard
            n_results (int): Number of results to return
            
        Returns:
            Dict[str, Any]: Search results
        """
        # Build where clause for filtering
        where = {}
        if category:
            where["category"] = category
        if pattern_type:
            where["pattern_type"] = pattern_type
        if min_severity is not None:
            where["severity"] = {"$gte": min_severity}
        if standard:
            where["standard"] = standard
            
        return self.vector_store.search(
            query=query,
            n_results=n_results,
            where=where
        )
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base.
        
        Returns:
            Dict[str, Any]: Knowledge base statistics
        """
        stats = self.vector_store.get_collection_stats()
        
        # Get category distribution
        results = self.vector_store.search(
            query="",  # Empty query to get all items
            n_results=1000  # Adjust based on your knowledge base size
        )
        
        categories = {}
        for metadata in results["metadatas"][0]:
            category = metadata.get("category", "unknown")
            categories[category] = categories.get(category, 0) + 1
        
        stats["categories"] = categories
        return stats
    
    def reset_knowledge_base(self) -> None:
        """Reset the knowledge base collection."""
        self.vector_store.delete_collection() 