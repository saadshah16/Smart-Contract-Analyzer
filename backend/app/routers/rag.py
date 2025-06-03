from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from ..rag import RAGService
import os
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

# Initialize router
router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
    responses={404: {"description": "Not found"}},
)

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
        stats = rag_service.get_collection_stats()
        return {
            "success": True,
            "stats": stats
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