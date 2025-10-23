import os
import logging
from typing import Any, Dict, List, Optional, cast

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools import StructuredTool
from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    TextLoader, PDFMinerLoader, Docx2txtLoader, CSVLoader, UnstructuredMarkdownLoader
)
from langchain_community.document_loaders.base import BaseLoader
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pydantic import BaseModel, Field, SecretStr

from backend.src.infrastructure.adapters.rag.rag_config import rag_settings
import hashlib
import json
# Configure logging
logger = logging.getLogger(__name__)

# --- Configuration ---
CHROMA_PERSIST_DIR = rag_settings.CHROMA_PERSIST_DIR
TEXT_FILES_DIR = rag_settings.TEXT_FILES_DIR
GOOGLE_API_KEY = rag_settings.GOOGLE_API_KEY  
EMBEDDING_MODEL = f"models/{rag_settings.GOOGLE_EMBEDDING_MODEL}"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 3
METADATA_FILE = os.path.join(CHROMA_PERSIST_DIR, "metadata.json")   

# --- Embedding Function ---
embedding_function = GoogleGenerativeAIEmbeddings(
    model=EMBEDDING_MODEL,
    google_api_key=cast(SecretStr, GOOGLE_API_KEY),
    task_type="retrieval_document",
)
# hashing function

def compute_file_hash(file_path: str) -> str:
    """Compute SHA256 hash for a file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

# Define retriever input schema
class RetrieverInput(BaseModel):
    query: str = Field(description="Search query string to find information in the documents.")

class DocumentProcessor:
    """Class to handle document processing, vectorization and retrieval."""
    
    def __init__(self):
        """Initialize the document processor with the configured settings."""
        self.persist_dir = CHROMA_PERSIST_DIR
        self.files_dir = TEXT_FILES_DIR
        self.vectorstore = self._initialize_vectorstore()
        
    def _initialize_vectorstore(self) -> Chroma:
        """Initialize the vector database, either by loading existing or creating new."""
        if os.path.exists(self.persist_dir) and os.listdir(self.persist_dir):
            logger.info("Loading existing Chroma database from %s", self.persist_dir)
            return Chroma(
                persist_directory=self.persist_dir,
                embedding_function=embedding_function
            )
        else:
            logger.info("Building new Chroma database at %s", self.persist_dir)
            if not os.path.exists(self.files_dir):
                logger.warning("Text files directory does not exist: %s", self.files_dir)
                os.makedirs(self.files_dir, exist_ok=True)
                return Chroma(
                    persist_directory=self.persist_dir,
                    embedding_function=embedding_function
                )
                
            file_paths = self._get_document_paths()
            if not file_paths:
                logger.warning("No documents found in %s", self.files_dir)
                return Chroma(
                    persist_directory=self.persist_dir,
                    embedding_function=embedding_function
                )
                
            documents = self._load_documents(file_paths)
            return self._create_vectorstore(documents)
    
    def _get_document_paths(self) -> List[str]:
        """Get paths of all supported documents in the files directory."""
        if not os.path.exists(self.files_dir):
            return []
            
        return [
            os.path.join(self.files_dir, f) 
            for f in os.listdir(self.files_dir)
            if os.path.isfile(os.path.join(self.files_dir, f)) and
            os.path.splitext(f.lower())[1] in rag_settings.ALLOWED_EXTENSIONS
        ]
    
    def _get_loader_for_file(self, file_path: str) -> Optional[BaseLoader]:
        """Get the appropriate document loader based on file extension."""
        _, ext = os.path.splitext(file_path.lower())
        
        try:
            if ext == ".txt":
                return TextLoader(file_path, encoding="utf-8")
            elif ext == ".pdf":
                return PDFMinerLoader(file_path)
            elif ext == ".docx":
                return Docx2txtLoader(file_path)
            elif ext == ".md":
                return UnstructuredMarkdownLoader(file_path)
            elif ext == ".csv":
                return CSVLoader(file_path)
            else:
                logger.warning(f"Unsupported file extension: {ext}")
                return None
        except Exception as e:
            logger.error(f"Error creating loader for {file_path}: {str(e)}")
            return None
            
    def _load_documents(self, file_paths: List[str]) -> List[Document]:
        """Load documents from multiple file paths with appropriate loaders."""
        all_docs = []
        for file_path in file_paths:
            try:
                loader = self._get_loader_for_file(file_path)
                if loader:
                    logger.info(f"Loading document: {file_path}")
                    docs = loader.load()
                    all_docs.extend(docs)
                    logger.info(f"Loaded {len(docs)} document chunks from {file_path}")
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {str(e)}")
                
        return all_docs
        
    def _create_vectorstore(self, documents: List[Document]) -> Chroma:
        """Create and persist a vector database from documents."""
        if not documents:
            logger.warning("No documents to vectorize")
            return Chroma(
                persist_directory=self.persist_dir,
                embedding_function=embedding_function
            )
            
        # Split documents
        logger.info(f"Splitting {len(documents)} documents into chunks")
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=CHUNK_SIZE, 
            chunk_overlap=CHUNK_OVERLAP
        )
        docs_splits = text_splitter.split_documents(documents)
        logger.info(f"Created {len(docs_splits)} document chunks")

        # Create and persist the vectorstore
        logger.info("Creating vector embeddings and storing in Chroma")
        vectorstore = Chroma.from_documents(
            documents=docs_splits,
            embedding=embedding_function,
            persist_directory=self.persist_dir,
        )

        logger.info("Vector database created and persisted successfully")
        
        return vectorstore
        
    def add_document(self, file_path: str) -> bool:
        """Add a new document to the vector database."""
        try:
            loader = self._get_loader_for_file(file_path)
            if not loader:
                logger.error(f"Unsupported file type: {file_path}")
                return False
                
            # Load and split the document
            docs = loader.load()
            text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=CHUNK_SIZE, 
                chunk_overlap=CHUNK_OVERLAP
            )
            docs_splits = text_splitter.split_documents(docs)
            
            # Add to existing vectorstore
            self.vectorstore.add_documents(docs_splits)
            logger.info(f"Added {len(docs_splits)} chunks from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add document {file_path}: {str(e)}")
            return False
            
    def get_retriever_tool(self) -> StructuredTool:
        """Create and return a retriever tool for the vectorstore."""
        retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": TOP_K_RESULTS}
        )
        
        # Create a structured tool for retrieval
        retriever_tool = StructuredTool.from_function(
            func=lambda query: retriever.invoke(query),
            name="Document_Retriever",
            description="""Searches through internal knowledge base documents to find relevant information
            based on your query. Returns content from documents that best match your question.""",
            args_schema=RetrieverInput,
        )

        return retriever_tool
        
    def search(self, query: str) -> List[Document]:
        """Direct search interface to retrieve documents."""
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": TOP_K_RESULTS})
        return retriever.invoke(query)


# Create singleton instance for reuse
document_processor = DocumentProcessor()

def get_retriever_tool() -> StructuredTool:
    """Public function to get the retriever tool."""
    return document_processor.get_retriever_tool()


if __name__ == "__main__":
    # Configure logging for direct script execution
    logging.basicConfig(level=logging.INFO)
    
    # This block allows you to test this file directly
    print("Testing retriever tool creation...")
    tool = get_retriever_tool()
    print("Tool created successfully!")
    print(f"Tool Name: {tool.name}")
    
    # Test a sample query if documents exist
    try:
        print("\nTesting search functionality...")
        results = document_processor.search("What is the main theme?")
        print(f"Found {len(results)} relevant documents")
        if results:
            print("\nFirst result preview:")
            print(results[0].page_content[:200] + "...")
    except Exception as e:
        print(f"Search test failed: {str(e)}")