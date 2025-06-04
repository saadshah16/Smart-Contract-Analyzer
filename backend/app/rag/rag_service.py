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
        """Retrieve relevant context from both contract store and knowledge base."""
        try:
            print("🔍 Retrieving context for:", question)
            
            # Get results from both collections
            contract_results = self.vector_store.search(question, n_results=2)
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