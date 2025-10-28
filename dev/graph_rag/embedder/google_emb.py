import os
from typing import Any, Dict, cast

from langchain.text_splitter import RecursiveCharacterTextSplitter
# Import the correct tool factory
from langchain.tools.retriever import create_retriever_tool
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
# We only need SecretStr from Pydantic
from pydantic import SecretStr

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

# --- DELETE THE RetrieverInput class ---
# The create_retriever_tool factory handles this for us.


# Initialize vectorstore and retriever at module level for reuse
def _initialize_vectorstore():
    """Initialize the vector store once at module level."""
    if os.path.exists(CHROMA_PERSIST_DIR):
        # 1. Load the existing database
        print("--- Loading existing Chroma database ---")
        vectorstore = Chroma(
            persist_directory=CHROMA_PERSIST_DIR,
            embedding_function=embedding_function
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
    
    return vectorstore

# Initialize once
_vectorstore = _initialize_vectorstore()
_retriever = _vectorstore.as_retriever(search_kwargs={"k": 2})

# Export this function so it can be imported directly
def retrieve_documents(query: str) -> str:
    """Retrieve documents based on a query string."""
    print(f"Executing document retrieval with query: '{query}'")
    docs = _retriever.invoke(query)
    if not docs:
        return "No relevant documents found."
        
    # Format results in a more readable way
    results = []
    for i, doc in enumerate(docs):
        # Extract source name from the path
        source = doc.metadata.get("source", "unknown")
        source_name = source.split("/")[-1] if "/" in source else source
        
        # Add formatted entry
        results.append(f"[Document {i+1} from {source_name}]:\n{doc.page_content}")
        
    return "\n\n".join(results)

def get_retriever_tool():
    """
    Creates and returns a retriever tool using the standard factory.
    """
    # Create a standard retriever tool using the retrieve_documents function
    from langchain.tools import Tool

    # Create a simplified wrapper tool that's easier to serialize
    retriever_tool = Tool.from_function(
        name="Document_Retriever",
        description="""Useful for answering questions about Alice in Wonderland and Project Gutenberg.
        Use this tool first before considering web search.""",
        func=retrieve_documents,
    )

    return retriever_tool

if __name__ == "__main__":
    # This block allows you to test this file directly
    print("Testing retriever tool creation...")
    tool = get_retriever_tool()
    print("Tool created successfully!")
    print(f"Tool Name: {tool.name}")