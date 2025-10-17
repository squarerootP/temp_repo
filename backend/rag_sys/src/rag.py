import os

from langchain import hub
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser

# Import your LLM as before
from backend.rag_sys.src.adapter.llms.cerebras import llm

# 1. Setup embedding and load vectorstore (no vectorization happens here)
embedding = HuggingFaceEmbeddings(
    model_name="google/embeddinggemma-300m"
)
# Error handling
if not os.path.exists("./chroma_db"):
    raise RuntimeError("Chroma vectorstore not found. Run your vectorizer script first to create the DB.")

vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embedding
)
retriever = vectorstore.as_retriever()

# 2. Load RAG prompt from LangChain Hub
rag_prompt = hub.pull("rlm/rag-prompt")

def format_docs(docs):
    """Format retrieved documents for the prompt context."""
    return "\n\n".join(doc.page_content for doc in docs)

# 3. Compose your RAG Chain (prompt -> LLM -> output parser)
rag_chain = rag_prompt | llm | StrOutputParser()

# 4. Define your query
query = "What are the major findings in ethnopharmacology over the last 10 years?"

# 5. Retrieve relevant documents from the vectorstore
docs_retrieved = retriever.get_relevant_documents(query)

# 6. Format the context for the prompt
context = format_docs(docs_retrieved)

# 7. Build input dictionary for the chain
inputs = {
    "question": query,
    "context": context
}

# 8. Run the RAG chain and print the answer
answer = rag_chain.invoke(inputs)
print(answer)