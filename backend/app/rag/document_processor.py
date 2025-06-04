from typing import List, Dict, Any, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
import uuid
import re
from datetime import datetime

class DocumentProcessor:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: Optional[List[str]] = None
    ):
        """Initialize the document processor.
        
        Args:
            chunk_size (int): Size of text chunks
            chunk_overlap (int): Overlap between chunks
            separators (Optional[List[str]]): List of separators for text splitting
        """
        if separators is None:
            separators = ["\n\n", "\n", ".", "!", "?", ",", " ", ""]
            
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len,
            is_separator_regex=False
        )
    
    def process_smart_contract(
        self,
        contract_text: str,
        contract_name: str,
        contract_address: Optional[str] = None,
        network: Optional[str] = None
    ) -> Dict[str, List]:
        """Process a smart contract text into chunks with metadata.
        
        Args:
            contract_text (str): The smart contract source code
            contract_name (str): Name of the contract
            contract_address (Optional[str]): Contract address if available
            network (Optional[str]): Network where contract is deployed
            
        Returns:
            Dict[str, List]: Dictionary containing processed documents, metadatas, and ids
        """
        # Split the contract into chunks
        chunks = self.text_splitter.split_text(contract_text)
        
        # Generate metadata and IDs for each chunk
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            # Generate a unique ID for the chunk
            chunk_id = str(uuid.uuid4())
            
            # Create metadata for the chunk
            metadata = {
                "contract_name": contract_name,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "source": "smart_contract",
                "timestamp": datetime.now().isoformat()
            }
            
            if contract_address:
                metadata["contract_address"] = contract_address
            if network:
                metadata["network"] = network
                
            # Add function signatures if present in the chunk
            function_sigs = self._extract_function_signatures(chunk)
            if function_sigs:
                metadata["functions"] = ", ".join(function_sigs)
            
            documents.append(chunk)
            metadatas.append(metadata)
            ids.append(chunk_id)
        
        return {
            "documents": documents,
            "metadatas": metadatas,
            "ids": ids
        }
    
    def _extract_function_signatures(self, text: str) -> List[str]:
        """Extract function signatures from a chunk of Solidity code.
        
        Args:
            text (str): Chunk of Solidity code
            
        Returns:
            List[str]: List of function signatures found in the text
        """
        # Basic regex pattern for Solidity function declarations
        # This is a simple pattern and might need to be enhanced for complex cases
        pattern = r"function\s+(\w+)\s*\([^)]*\)\s*(?:public|private|internal|external)?\s*(?:view|pure|payable)?\s*(?:returns\s*\([^)]*\))?"
        
        matches = re.finditer(pattern, text)
        return [match.group(0) for match in matches] 