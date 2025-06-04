from typing import List, Dict, Any, Optional
from .vector_store import VectorStoreManager
from .document_processor import DocumentProcessor
from .knowledge_base import KnowledgeBaseManager
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain_anthropic import ChatAnthropic
import os
import traceback
import json
import anthropic

# Configure logger for this module - moved from __init__
import logging
logger = logging.getLogger(__name__)

class RAGService:
    def __init__(
        self,
        persist_directory: str = "chroma_db",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """Initialize the RAG service.
        
        Args:
            persist_directory: Directory to persist the vector store
            chunk_size: Size of text chunks for splitting
            chunk_overlap: Overlap between chunks
        """
        self.vector_store = VectorStoreManager(persist_directory=persist_directory)
        self.knowledge_base = KnowledgeBaseManager(persist_directory=persist_directory)
        self.document_processor = DocumentProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # Initialize the language model
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert smart contract analyzer. Your task is to answer questions about smart contracts based on the provided context.
            
            Guidelines:
            1. Use both the contract context and knowledge base context to provide comprehensive answers
            2. Highlight any security concerns or best practices from the knowledge base
            3. If a vulnerability is mentioned, include its severity and potential impact
            4. When possible, provide code examples from the knowledge base
            5. If the context doesn't contain enough information, say so
            6. Be precise and technical in your explanations
            7. Explain complex concepts in a clear and structured way
            
            Context: {context}
            
            Question: {question}"""),
            ("human", "{question}")
        ])
        
        # Create the RAG chain
        self.chain = (
            # Updated chain to pass question and optionally contract_name to context retrieval
            {
                "context": (lambda x: self._retrieve_context(x["question"], x.get("contract_name"))),
                "question": RunnablePassthrough()
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
    
    def add_contract(
        self,
        contract_text: str,
        contract_name: str,
        contract_address: Optional[str] = None,
        network: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a smart contract to the vector store.
        
        Args:
            contract_text (str): The smart contract source code
            contract_name (str): Name of the contract
            contract_address (Optional[str]): Contract address if available
            network (Optional[str]): Network where contract is deployed
            
        Returns:
            Dict[str, Any]: Statistics about the added documents
        """
        try:
            print("🧪 Starting add_contract...")
            print("Contract Name:", contract_name)
            print("Length of contract_text:", len(contract_text))
            logger.info(f"Attempting to add contract: {contract_name}")

            processed = self.document_processor.process_smart_contract(
                contract_text=contract_text,
                contract_name=contract_name,
                contract_address=contract_address,
                network=network
            )

            print("✅ Document processing successful!")
            logger.info(f"Document processing successful for {contract_name}")

            self.vector_store.add_documents(
                documents=processed["documents"],
                metadatas=processed["metadatas"],
                ids=processed["ids"]
            )

            print("✅ Documents added to vector store.")
            logger.info(f"Documents added to vector store for {contract_name}")

            return self.vector_store.get_collection_stats()

        except Exception as e:
            print("🔥 ERROR in RAGService.add_contract")
            traceback.print_exc()
            logger.error(f"Error adding contract {contract_name}: {e}")
            raise e
    
    def _retrieve_context(self, question: str, contract_name: Optional[str] = None) -> str:
        """Retrieve relevant context from both contract store and knowledge base."""
        try:
            print("🔍 Retrieving context for:", question)
            
            # Get results from both collections
            # Perform a filtered search on the contract store if contract_name is provided
            contract_filter = {"contract_name": contract_name} if contract_name else {}
            contract_results = self.vector_store.search(query=question, n_results=5, where=contract_filter)
            knowledge_results = self.knowledge_base.search_knowledge(question, n_results=2)
            
            context_parts = []
            
            # Add contract context
            for doc, metadata in zip(contract_results["documents"][0], contract_results["metadatas"][0]):
                context_part = f"From Contract {metadata.get('contract_name', 'Unknown')}"
                if "functions" in metadata:
                    context_part += f" (Functions: {', '.join(metadata['functions'])})"
                context_part += f":\n{doc}\n"
                context_parts.append(context_part)
            
            # Add knowledge base context
            for doc, metadata in zip(knowledge_results["documents"][0], knowledge_results["metadatas"][0]):
                context_part = f"Knowledge Base ({metadata.get('category', 'Unknown')})"
                if metadata.get('severity'):
                    context_part += f" [Severity: {metadata['severity']}/5]"
                if metadata.get('code_example'):
                    context_part += f"\nExample Implementation:\n{metadata['code_example']}"
                if metadata.get('description'):
                    context_part += f"\nDescription: {metadata['description']}"
                context_part += f":\n{doc}\n"
                context_parts.append(context_part)
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            print("🔥 ERROR in _retrieve_context")
            traceback.print_exc()
            raise e
    
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
        """Add an item to the knowledge base."""
        return self.knowledge_base.add_knowledge_item(
            content=content,
            category=category,
            pattern_type=pattern_type,
            severity=severity,
            standard=standard,
            version=version,
            references=references,
            code_example=code_example,
            description=description
        )
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        return self.knowledge_base.get_knowledge_stats()
    
    def reset_knowledge_base(self) -> None:
        """Reset the knowledge base collection."""
        self.knowledge_base.reset_knowledge_base()
    
    def query(self, question: str) -> str:
        """Query the RAG system with a question.
        
        Args:
            question (str): The user's question about the smart contract
            
        Returns:
            str: The generated answer
        """
        try:
            print("🧠 Received query:", question)
            # The chain now expects a dict with 'question' and optional 'contract_name'
            # Since the original /query endpoint only takes a question, we'll call it like this
            # For targeted queries from the frontend, we will need to update the frontend
            response = self.chain.invoke({"question": question})
            print("✅ Chain response:", response)
            return response
        except Exception as e:
            print("🔥 ERROR in RAGService.query")
            traceback.print_exc()
            raise e
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store collection.
        
        Returns:
            Dict[str, Any]: Collection statistics
        """
        return self.vector_store.get_collection_stats()
    
    def get_contract_details(self) -> List[Dict[str, Any]]:
        """Get detailed information about all stored contracts.
        
        Returns:
            List[Dict[str, Any]]: List of contract details including metadata
        """
        try:
            # Get all documents from the collection
            results = self.vector_store.get_all_documents()
            
            # Process and deduplicate contracts based on contract_name
            contracts = {}
            # Iterate directly over the lists of documents and metadatas
            documents = results.get("documents", [])
            metadatas = results.get("metadatas", [])
            
            for doc, metadata in zip(documents, metadatas):
                # Ensure metadata is a dictionary before accessing keys
                if not isinstance(metadata, dict):
                    print(f"Warning: Skipping metadata that is not a dictionary: {metadata}")
                    continue # Skip this item if metadata is not a dict

                contract_name = metadata.get("contract_name")
                if not contract_name:
                    continue
                    
                if contract_name not in contracts:
                    contracts[contract_name] = {
                        "id": metadata.get("id", ""),
                        "name": contract_name,
                        "address": metadata.get("contract_address"),
                        "network": metadata.get("network"),
                        "addedAt": metadata.get("timestamp", ""),
                        "lastAnalyzed": metadata.get("last_analyzed", ""),
                        "functions": metadata.get("functions", []),
                        "document_count": 1
                    }
                else:
                    contracts[contract_name]["document_count"] += 1
                    # Update last analyzed timestamp if newer
                    if metadata.get("last_analyzed"):
                        current_last = contracts[contract_name]["lastAnalyzed"]
                        if not current_last or metadata["last_analyzed"] > current_last:
                            contracts[contract_name]["lastAnalyzed"] = metadata["last_analyzed"]
            
            return list(contracts.values())
            
        except Exception as e:
            print("🔥 ERROR in get_contract_details")
            traceback.print_exc()
            raise e
    
    def reset_collection(self) -> None:
        """Reset the vector store collection."""
        self.vector_store.delete_collection()

    def analyze_contract_with_claude(self, contract_text: str) -> List[Dict[str, Any]]:
        """Analyze contract using Claude"""
        
        if not self.llm:
            raise ValueError("Anthropic API client not configured.")

        prompt = f"""
You are an expert legal analyst specializing in contract review for non-lawyers.
Your job is to make complex legal language accessible and highlight potential risks.

Analyze the following contract and break it down into numbered clauses.
For each significant clause, return a JSON object with the structure shown below.

Important guidelines:
1. Focus on the most important clauses (aim for 5-15 clauses total)
2. Skip boilerplate sections like signatures, dates, and standard formatting
3. Prioritize clauses that involve rights, obligations, payments, termination, liability, etc.
4. For risk_flag, use "Yes" only for genuine concerns that a non-lawyer should be aware of
5. Keep explanations clear and accessible to non-lawyers

Return ONLY a valid JSON array in this exact format:

[{{
  "clause_number": 1,
  "original_clause": "The exact text of the clause from the contract",
  "explanation": "Clear explanation in plain English of what this clause means",
  "risk_flag": "Yes or No",
  "risk_reason": "Explanation of the risk (only include if risk_flag is Yes)"
}}]

Contract text to analyze:

{contract_text[:8000]}  # Limit to prevent token overflow
        """

        try:
            logger.info("Sending analysis request to Claude API")
            # Use invoke for the Langchain ChatAnthropic object
            message = self.llm.invoke([{"role": "user", "content": prompt}])

            # For invoke, content is directly in .content attribute (which is a string for text responses)
            response_text = message.content
            logger.info(f"Received analysis response from Claude API: {len(response_text)} characters")

            # Attempt to extract JSON from Claude response
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1

            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                parsed_result = json.loads(json_str)
                
                # Validate the structure
                if not isinstance(parsed_result, list):
                    raise ValueError("Analysis response is not a JSON array")
                
                for item in parsed_result:
                    required_fields = ["clause_number", "original_clause", "explanation", "risk_flag"]
                    for field in required_fields:
                        if field not in item:
                            raise ValueError(f"Missing required field: {field} in analysis item")
                
                logger.info(f"Successfully parsed {len(parsed_result)} analysis clauses")
                return parsed_result
            else:
                logger.error("No JSON array found in Claude's analysis response")
                raise ValueError("No valid JSON array found in AI analysis response")

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in analysis: {e}")
            logger.error(f"Raw analysis response: {response_text[:500]}...")
            raise e
        except anthropic.APIError as e:
            logger.error(f"Anthropic API Error during analysis: {e}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error during Claude analysis: {e}")
            raise e

    def analyze_stored_contract(self, contract_name: str) -> List[Dict[str, Any]]:
        """Retrieve and analyze a stored smart contract.
        
        Args:
            contract_name (str): The name of the contract to analyze.
            
        Returns:
            List[Dict[str, Any]]: The analysis results.
        """
        try:
            logger.info(f"Retrieving chunks for contract: {contract_name}")
            results = self.vector_store.get_documents_by_metadata(
                metadata_filter={
                    "contract_name": contract_name
                },
                include=["documents", "metadatas"]
            )

            documents = results.get("documents", [])
            metadatas = results.get("metadatas", [])

            if not documents:
                raise ValueError(f"No chunks found for contract: {contract_name}")

            # Combine documents and metadatas, then sort by chunk_index
            chunks_with_metadata = sorted(
                zip(documents, metadatas),
                key=lambda item: item[1].get("chunk_index", 0)
            )

            # Reconstruct the full contract text
            full_contract_text = "\n".join([doc for doc, metadata in chunks_with_metadata])

            logger.info(f"Reconstructed contract text ({len(full_contract_text)} chars). Starting analysis.")

            # Analyze the reconstructed text
            analysis_result = self.analyze_contract_with_claude(full_contract_text)

            logger.info(f"Analysis completed for stored contract: {contract_name}")

            return analysis_result

        except Exception as e:
            logger.error(f"Error analyzing stored contract {contract_name}: {e}")
            raise e 