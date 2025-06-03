from typing import List, Dict, Any, Optional
from .vector_store import VectorStoreManager
from .document_processor import DocumentProcessor
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain_anthropic import ChatAnthropic
import os
import traceback

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
            1. Use the provided context to answer questions accurately
            2. If the context doesn't contain enough information, say so
            3. Be precise and technical in your explanations
            4. Highlight any potential security concerns or best practices
            5. Explain complex concepts in a clear and structured way
            
            Context: {context}
            
            Question: {question}"""),
            ("human", "{question}")
        ])
        
        # Create the RAG chain
        self.chain = (
            {"context": self._retrieve_context, "question": RunnablePassthrough()}
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

            processed = self.document_processor.process_smart_contract(
                contract_text=contract_text,
                contract_name=contract_name,
                contract_address=contract_address,
                network=network
            )

            print("✅ Document processing successful!")

            self.vector_store.add_documents(
                documents=processed["documents"],
                metadatas=processed["metadatas"],
                ids=processed["ids"]
            )

            print("✅ Documents added to vector store.")

            return self.vector_store.get_collection_stats()

        except Exception as e:
            print("🔥 ERROR in RAGService.add_contract")
            traceback.print_exc()
            raise e
    
    def _retrieve_context(self, question: str) -> str:
        try:
            print("🔍 Retrieving context for:", question)
            results = self.vector_store.search(question, n_results=3)
            print("📊 Search results:", results)

            context_parts = []
            for doc, metadata in zip(results["documents"][0], results["metadatas"][0]):
                context_part = f"From {metadata.get('contract_name', 'Unknown')}"
                if "functions" in metadata:
                    context_part += f" (Functions: {', '.join(metadata['functions'])})"
                context_part += f":\n{doc}\n"
                context_parts.append(context_part)

            return "\n\n".join(context_parts)
        except Exception as e:
            print("🔥 ERROR in _retrieve_context")
            traceback.print_exc()
            raise e

    
    def query(self, question: str) -> str:
        """Query the RAG system with a question.
        
        Args:
            question (str): The user's question about the smart contract
            
        Returns:
            str: The generated answer
        """
        try:
            print("🧠 Received query:", question)
            response = self.chain.invoke(question)
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
    
    def reset_collection(self) -> None:
        """Reset the vector store collection."""
        self.vector_store.delete_collection() 