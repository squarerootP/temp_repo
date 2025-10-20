import os
from typing import cast

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pydantic import SecretStr

from backend.src.infrastructure.config.settings import api_settings

# --- Configuration ---
# It's good practice to define constants at the top
CHROMA_PERSIST_DIR = "./chroma_db"
TEXT_FILES = ["data/alice_in_wonderland.txt", "data/gutenberg.txt"]
GOOGLE_API_KEY = api_settings.GOOGLE_GENAI_API_KEY
EMBEDDING_MODEL = f"models/{api_settings.GOOGLE_EMBEDDING_MODEL}"

# --- Embedding Function ---
embedding_function = GoogleGenerativeAIEmbeddings(
    model=EMBEDDING_MODEL,
    google_api_key=cast(SecretStr, GOOGLE_API_KEY),
    task_type="retrieval_document",
)

def get_retriever_tool():
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
            embedding_function=embedding_function
        )
    else:
        # 2. Build the database if it doesn't exist
        print("--- Building new Chroma database ---")
        # Load documents
        all_docs = []
        for file_path in TEXT_FILES:
            loader = TextLoader(file_path, encoding="utf-8") # Use 'utf-8', the canonical name
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
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    retriever_tool = create_retriever_tool(
        retriever=retriever,
        name="Document_Retriever",
        description="Useful for answering questions about Alice in Wonderland and other classic texts.",
    )
    return retriever_tool

if __name__ == "__main__":
    # This block allows you to test this file directly
    print("Testing retriever tool creation...")
    tool = get_retriever_tool()
    print("Tool created successfully!")
    print(f"Tool Name: {tool.name}")
    # Example query
    # result = tool.invoke({"input": "Who is Alice?"})
    # print(result)