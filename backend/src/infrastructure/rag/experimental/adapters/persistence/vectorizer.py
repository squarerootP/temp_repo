import os

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pypdf.errors import PdfStreamError
from tqdm import tqdm

from backend.rag_sys.src.infrastructure.settings import env_settings

google_genai_api_key = env_settings.GOOGLEAI_API_KEY

pdf_files = [
    r"C:\Users\phongnv37\fastapi-stud\backend\rag_sys\data\10 YEARS OF ETHNOPHARMACOLOGY.PDF",
    r"C:\Users\phongnv37\fastapi-stud\backend\rag_sys\data\10 YEARS OF GASTROINTESTINAL .PDF",
]
persist_dir = "./chroma_db"

docs = []
# Track PDF loading progress
for pdf_path in tqdm(pdf_files, desc="Loading PDFs"):
    try:
        docs.extend(PyPDFLoader(pdf_path).load())
    except PdfStreamError:
        print(f"Skipping corrupted PDF: {pdf_path}")

# Track conversion to Document objects
docs_list = []
for doc in tqdm(docs, desc="Converting to Document objects"):
    docs_list.append(Document(page_content=doc.page_content, metadata=doc.metadata))

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=512, chunk_overlap=20
)

# Track document splitting progress
docs_splits = []
for split_docs in tqdm(text_splitter.split_documents(docs_list), desc="Splitting documents"):
    docs_splits.append(split_docs)

embedding = HuggingFaceEmbeddings(
    model_name="Qwen/Qwen3-Embedding-0.6B"
)

# Track vectorstore creation progress (optional since it's often a single call)
vectorstore = Chroma.from_documents(
    documents=docs_splits,
    embedding=embedding,
    persist_directory=persist_dir
)