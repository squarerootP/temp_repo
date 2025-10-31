import os
from functools import lru_cache
from typing import Any, Dict, Optional, cast

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools import StructuredTool, Tool, tool
from langchain.tools.retriever import create_retriever_tool
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pydantic import BaseModel, Field, SecretStr

from backend.src.infrastructure.adapters.document_hasher import DocumentHasher
from backend.src.infrastructure.config.settings import (api_settings,
                                                        db_settings,
                                                        rag_settings)
from backend.src.application.interfaces.rag_interfaces.vectorstore_repo import IVectorStoreRepository
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import Optional, List
from langchain_core.documents import Document

# --- Configuration ---
CHROMA_PERSIST_DIR = rag_settings.CHROMA_PERSIST_DIR
METADATA_FILE = os.path.join(CHROMA_PERSIST_DIR, "document_metadata.json")
TEXT_FILES_DIR = rag_settings.TEXT_FILES_DIR
TEXT_FILES = [
    "data/alice_in_wonderland.txt",
    "data/frankeinstein.txt",
    "data/gutenberg.txt",
    "data/mobydick_or_the_white_whale.txt",
    "data/price_and_prejudice.txt", 
    "data/romeo_and_juliet.txt"
]
GOOGLE_API_KEY = api_settings.GOOGLE_API_KEY
EMBEDDING_MODEL = f"models/{api_settings.GOOGLE_EMBEDDING_MODEL}"

# --- Embedding Function ---
@lru_cache(maxsize=1)
def get_embedding_function() -> GoogleGenerativeAIEmbeddings:
    embedding_function = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=cast(SecretStr, GOOGLE_API_KEY),
        task_type="retrieval_document",
    )
    # Test embedding
    test_text = "This is a test embedding."
    test_embedding = embedding_function.embed_query(test_text)
    print(f"Embedding test successful. Vector dimension: {len(test_embedding)}")
    
    return embedding_function

embedding_function = get_embedding_function()



class RetrieverInput(BaseModel):
    query: str = Field(description="The query to search for in the documents")

def get_retriever_tool(vector_store_repo: IVectorStoreRepository, document_hash: Optional[str] = None) -> StructuredTool:
    """
    Creates a retriever tool that uses the provided vector store repository.
    """
    def retrieve(query: str) -> List[Document]:
        print(f"Retrieve called with document_hash: {document_hash!r}")  # !r shows quotes
        if document_hash is not None:
            print("Using get_document_chunks")
            return vector_store_repo.get_document_chunks(query, document_hash)
        print("Using get_similar_chunks")
        return vector_store_repo.get_similar_chunks(query)
            
    return StructuredTool.from_function(
        func=retrieve,
        name="Retriever",
        description="Retrieves relevant information from stored documents",
        args_schema=RetrieverInput
    )