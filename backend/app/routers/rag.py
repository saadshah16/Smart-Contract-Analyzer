from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from ..rag import RAGService
import os
from dotenv import load_dotenv
import traceback
import logging

# Load environment variables
load_dotenv()

# Initialize router
router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
    responses={404: {"description": "Not found"}},
)

# Configure logger for this module
logger = logging.getLogger(__name__)

# Initialize RAG service
rag_service = RAGService(
    persist_directory=os.getenv("CHROMA_PERSIST_DIR", "chroma_db")
)

class ContractInput(BaseModel):
    contract_text: str
    contract_name: str
    contract_address: Optional[str] = None
    network: Optional[str] = None

class QueryInput(BaseModel):
    question: str
    contract_name: Optional[str] = None

class KnowledgeBaseItem(BaseModel):
    content: str
    category: str
    pattern_type: str
    severity: int = 0
    standard: Optional[str] = None
    version: Optional[str] = None
    references: Optional[List[str]] = None
    code_example: Optional[str] = None
    description: Optional[str] = None

class StoredContractAnalysisInput(BaseModel):
    contract_name: str

@router.post("/add-contract")
async def add_contract(contract: ContractInput) -> Dict[str, Any]:
    """Add a smart contract to the RAG system."""
    try:
        stats = rag_service.add_contract(
            contract_text=contract.contract_text,
            contract_name=contract.contract_name,
            contract_address=contract.contract_address,
            network=contract.network
        )
        return {
            "success": True,
            "message": "Contract added successfully",
            "stats": stats
        }
    except Exception as e:
        print("🔥 ERROR IN /add-contract ENDPOINT:")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error adding contract: {str(e)}"
        )

@router.post("/query")
async def query_contract(query: QueryInput) -> Dict[str, Any]:
    """Query the RAG system about a smart contract."""
    try:
        print("📥 Incoming query to /rag/query:", query.question)
        answer = rag_service.query(query.question)
        print("✅ Query processed successfully")
        return {
            "success": True,
            "answer": answer
        }
    except Exception as e:
        print("🔥 ERROR IN /rag/query ENDPOINT:")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error querying contract: {str(e)}"
        )

@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    """Get statistics about the RAG system."""
    try:
        # Get basic collection stats
        collection_stats = rag_service.get_collection_stats()
        
        # Get detailed contract information
        contracts = rag_service.get_contract_details()
        
        return {
            "success": True,
            "stats": {
                "total_contracts": collection_stats["count"],
                "collection_name": collection_stats["name"],
                "contracts": contracts
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting stats: {str(e)}"
        )

@router.post("/reset")
async def reset_collection() -> Dict[str, Any]:
    """Reset the RAG system collection."""
    try:
        rag_service.reset_collection()
        return {
            "success": True,
            "message": "Collection reset successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error resetting collection: {str(e)}"
        )

@router.post("/knowledge/add")
async def add_knowledge_item(item: KnowledgeBaseItem) -> Dict[str, Any]:
    """Add an item to the knowledge base."""
    try:
        result = rag_service.add_knowledge_item(
            content=item.content,
            category=item.category,
            pattern_type=item.pattern_type,
            severity=item.severity,
            standard=item.standard,
            version=item.version,
            references=item.references,
            code_example=item.code_example,
            description=item.description
        )
        return {
            "success": True,
            "message": "Knowledge item added successfully",
            "item": result
        }
    except Exception as e:
        print("🔥 ERROR IN /knowledge/add ENDPOINT:")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error adding knowledge item: {str(e)}"
        )

@router.get("/knowledge/stats")
async def get_knowledge_stats() -> Dict[str, Any]:
    """Get statistics about the knowledge base."""
    try:
        stats = rag_service.get_knowledge_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting knowledge stats: {str(e)}"
        )

@router.post("/knowledge/reset")
async def reset_knowledge_base() -> Dict[str, Any]:
    """Reset the knowledge base collection."""
    try:
        rag_service.reset_knowledge_base()
        return {
            "success": True,
            "message": "Knowledge base reset successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error resetting knowledge base: {str(e)}"
        )

@router.post("/analyze-stored")
async def analyze_stored_contract_endpoint(input: StoredContractAnalysisInput) -> Dict[str, Any]:
    """Analyze a smart contract already stored in the RAG system."""
    try:
        logger.info(f"Received request to analyze stored contract: {input.contract_name}")
        analysis_result = rag_service.analyze_stored_contract(input.contract_name)
        logger.info(f"Analysis complete for stored contract: {input.contract_name}")
        return {
            "success": True,
            "message": "Stored contract analyzed successfully",
            "analysis": analysis_result
        }
    except ValueError as e:
        logger.error(f"Error analyzing stored contract {input.contract_name}: {e}")
        raise HTTPException(
            status_code=404, # Use 404 if the contract name is not found
            detail=f"Contract not found: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error analyzing stored contract {input.contract_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing stored contract: {str(e)}"
        ) 