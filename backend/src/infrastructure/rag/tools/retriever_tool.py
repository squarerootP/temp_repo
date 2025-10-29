import os
from typing import Any, Dict, Optional, cast

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools import StructuredTool, Tool, tool
from langchain.tools.retriever import create_retriever_tool
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pydantic import BaseModel, Field, SecretStr

from backend.src.infrastructure.config.settings import api_settings

# --- Configuration ---
CHROMA_PERSIST_DIR = "./chroma_db"
TEXT_FILES = ["data/alice_in_wonderland.txt", "data/gutenberg.txt"]
GOOGLE_API_KEY = api_settings.GOOGLE_API_KEY
EMBEDDING_MODEL = f"models/{api_settings.GOOGLE_EMBEDDING_MODEL}"

# --- Embedding Function ---
embedding_function = GoogleGenerativeAIEmbeddings(
    model=EMBEDDING_MODEL,
    google_api_key=cast(SecretStr, GOOGLE_API_KEY),
    task_type="retrieval_document",
)

# Define explicit schema with valid field name
class RetrieverInput(BaseModel):
    query: str = Field(description="Search query string to find information in the documents.")


def get_retriever_tool(doc_hash: Optional[str]) -> Tool:
    """
    Creates and returns a retriever tool.
    If the vector database exists, it loads it.
    If not, it builds the database from the source documents.
    """
    if os.path.exists(CHROMA_PERSIST_DIR):
        # 1. Load the existing database
        print("--- Loading existing Chroma database ---")
        vectorstore = Chroma(
            persist_directory=CHROMA_PERSIST_DIR,
            embedding_function=embedding_function,
        )
    else:
        # 2. Build the database if it doesn't exist
        print("--- Building new Chroma database ---")
        # Load documents
        all_docs = []
        for file_path in TEXT_FILES:
            loader = TextLoader(file_path, encoding="utf-8")
            all_docs.extend(loader.load())

        # Split documents
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=512, chunk_overlap=20
        )
        docs_splits = text_splitter.split_documents(all_docs)

        # Create and persist the vectorstore
        vectorstore = Chroma.from_documents(
            documents=docs_splits,
            embedding=embedding_function,
            persist_directory=CHROMA_PERSIST_DIR,
        )

    # 3. Create the retriever and the tool
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 2,
        doc_hash: doc_hash} if doc_hash else {"k": 2})
    
    # Create a tool using create_retriever_tool for consistent parameter handling
    retriever_tool = StructuredTool.from_function(
        func=lambda query: retriever.invoke(query),
        name="Document_Retriever",
        description="""Useful for answering questions about Alice in Wonderland and Project Gutenberg.
        Use this tool first before considering web search.""",
        args_schema=RetrieverInput,
    )

    return retriever_tool #type: ignore
