import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS  # Change to FAISS
from pypdf.errors import PdfStreamError
from langchain.embeddings import HuggingFaceEmbeddings

pdf_files = [
    r"C:\Users\phongnv37\fastapi-stud\backend\rag_sys\data\doc1.PDF",
    r"C:\Users\phongnv37\fastapi-stud\backend\rag_sys\data\doc2.PDF",
]

# For FAISS, we'll save the index to this file
faiss_index_path = "./faiss_index"

docs = []
for pdf_path in pdf_files:
    try:
        docs.extend(PyPDFLoader(pdf_path).load())
    except PdfStreamError:
        print(f"Skipping corrupted PDF: {pdf_path}")
    except FileNotFoundError:
        print(f"File not found: {pdf_path}")
    except Exception as e:
        print(f"Error loading {pdf_path}: {e}")

if not docs:
    raise ValueError("No documents loaded! Please check your PDF files.")

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=768, chunk_overlap=80
)
docs_splits = text_splitter.split_documents(docs)

embedding_model = HuggingFaceEmbeddings(
    model_name="google/embeddinggemma-300m",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

# Create FAISS index from documents
vectorstore = FAISS.from_documents(
    documents=docs_splits,
    embedding=embedding_model
)

# Save the FAISS index to disk
vectorstore.save_local(faiss_index_path)

print(f"FAISS index saved to {faiss_index_path}")