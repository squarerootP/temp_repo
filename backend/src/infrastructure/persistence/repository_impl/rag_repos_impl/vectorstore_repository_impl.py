import gc
import hashlib
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
import chromadb

import chardet
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document as LCDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.src.application.interfaces.library_interfaces.book_repository import BookRepository
from backend.src.application.interfaces.rag_interfaces.vectorstore_repo import \
    IVectorStoreRepository
from backend.src.domain.entities.rag_entities.document import Document
from backend.src.infrastructure.adapters.document_hasher import DocumentHasher
from backend.src.infrastructure.config.settings import rag_settings
from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.tools.doc_retriever_tool import \
    get_embedding_function
from backend.src.application.interfaces.rag_interfaces.document_repository import IDocumentRepository
from backend.src.utils import get_isbn13
TEXT_FILES_DIR = rag_settings.TEXT_FILES_DIR
CHROMA_PERSIST_DIR = rag_settings.CHROMA_PERSIST_DIR
TEXT_FILES = [
    os.path.join(TEXT_FILES_DIR, f)
    for f in os.listdir(TEXT_FILES_DIR)
    if os.path.isfile(os.path.join(TEXT_FILES_DIR, f)) and f.lower().endswith(".txt")
]
print("=== Text files to process:", TEXT_FILES)


def clean_file_name(name: str):
    name = os.path.splitext(name)[0] # removing the extension
    name = name.replace("_", " ").title()
    return name

class ChromaVectorStoreRepositoryImpl(IVectorStoreRepository):
    """Concrete vector store repository using Chroma and Google embeddings."""

    def __init__(self, doc_repo: IDocumentRepository,
                 book_repo: BookRepository, 
                 persist_directory: str = rag_settings.CHROMA_PERSIST_DIR):
        
        self.doc_repo = doc_repo
        self.book_repo = book_repo
        self.persist_directory = persist_directory
        self.metadata_file = os.path.join(persist_directory, "document_metadata.json")
        
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        self.text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=rag_settings.CHUNK_SIZE,
            chunk_overlap=rag_settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""],
            keep_separator=True,
        )

        self.embeddings = None
        self.current_document_hash: Optional[str] = None
        self.processed_documents: Dict[str, Dict[str, Any]] = {}

        self.collections: Dict[str, Any] = {
            "book_chunks": self.client.get_or_create_collection(
                "book_chunks",
                metadata={"hnsw:space": "cosine"}  # Use cosine distance
            ),
            "summary_chunks": self.client.get_or_create_collection(
                "summary_chunks", 
                metadata={"hnsw:space": "cosine"}
            ),
        }

        self._load_metadata()
        self._load_vectorstore()

    def _load_metadata(self):
        """Load document metadata from JSON file"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, "r") as f:
                    self.processed_documents = json.load(f)
                print(
                    f"✓ Loaded metadata for {len(self.processed_documents)} documents"
                )
            except Exception as e:
                print(f"⚠️  Failed to load metadata: {e}")
                self.processed_documents = {}

    def _save_metadata(self):
        """Save document metadata to JSON file"""
        try:
            os.makedirs(self.persist_directory, exist_ok=True)
            with open(self.metadata_file, "w") as f:
                json.dump(self.processed_documents, f, indent=2, default=str)
        except Exception as e:
            print(f"⚠️  Failed to save metadata: {e}")

    def _load_vectorstore(self):
        self.embeddings = self._initialize_embeddings()
        book_collection = self.collections["book_chunks"]
        summary_collection = self.collections["summary_chunks"]
        
        for text_file_path in TEXT_FILES:
            file_hash = DocumentHasher.hash_file(text_file_path)
            if file_hash in self.processed_documents:
                continue
            
            print(f"Embedding new doc: {text_file_path}")
            cleaned_file_name = clean_file_name(os.path.basename(text_file_path))
            
            document = self.process_document(text_file_path, file_hash, cleaned_file_name)
            self.doc_repo.save_document(document)
            
            retries = len(cleaned_file_name.split())
            for i in range(retries):
                cropping = " ".join(cleaned_file_name.split()[:retries-i])
                isbn = get_isbn13(cropping)
                if isbn:
                    break
                
            if not isbn:
                raise ValueError("isbn werent detected, check your file path", os.path.basename(text_file_path))
            db_book = self.book_repo.get_by_isbn(isbn)
            if not db_book:
                raise ValueError("no book found of such isbn, recheck your algorithm")
            summary_text = self.book_repo.get_by_isbn(isbn).summary or ""
            
            if summary_text:
                summary_embedding = self.embeddings.embed_query(summary_text)
                summary_collection.add(
                    ids=[isbn],
                    embeddings=[summary_embedding],
                    documents=[summary_text],
                    metadatas=[{
                        'isbn': isbn, 
                        "title": cleaned_file_name
                    }]
                )
        print(f"✓ Book chunks collection now has {book_collection.count()} items")
        print(f"✓ Summary collection now has {summary_collection.count()} items")

    def _initialize_embeddings(self):
        return get_embedding_function()

    # ==== CORE METHODS ====
    def process_document(self, file_path: str, hash: str, file_name: str) -> Document:
        """Load, hash, chunk, and prepare a document for storage."""

        try:
            # Read file
            with open(file_path, "rb") as file:
                raw_data = file.read()
                result = chardet.detect(raw_data)
            encoding = result["encoding"] if result["encoding"] else "utf-8"
            with open(file_path, "r", encoding=encoding) as file:
                content = file.read()
                
            # Load and chunk
            documents = TextLoader(file_path, encoding="utf-8").load()
            chunks = self.text_splitter.split_documents(documents)

            for i, chunk in enumerate(chunks):
                chunk.metadata.update(
                    {
                        "document_hash": hash,
                        "chunk_id": f"{hash[:8]}_chunk_{i}",
                        "source_file": file_name,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                    }
                )

            self.add_chunks_to_vectorstore("book_chunks",chunks)
            
            self.processed_documents[hash] = {
                "filename": file_name,
                "chunk_count": len(chunks),
                "chunk_ids": [chunk.metadata["chunk_id"] for chunk in chunks],
            }

            self._save_metadata()

            document_entity = Document(
                book_isbn=get_isbn13(file_name),
                title=file_name,
                content=content,
                hash=hash,
            )

            return document_entity
        except Exception as e:
            raise RuntimeError(f"Failed to process document {file_path}: {e}")

    def add_chunks_to_vectorstore(self, collection_name: str, chunks: List[LCDocument]):
        """Add new chunks to existing vectorstore"""
        collection = self.collections[collection_name]
        embeddings = self.embeddings.embed_documents([chunk.page_content for chunk in chunks])
        
        collection.add(
            ids=[chunk.metadata['chunk_id'] for chunk in chunks],
            embeddings=embeddings,
            documents=[chunk.page_content for chunk in chunks],
            metadatas=[chunk.metadata for chunk in chunks]
        )
        

    def get_similar_chunks(
        self, 
        query: str, 
        k: int = 4, 
        threshold: float = 0.7, 
        collection_name: str = "book_chunks", 
        filter_dict: dict = None
    ) -> List[LCDocument]:
        """Get similar chunks for a query with optional metadata filtering and proper distance handling"""
        
        collection = self.collections[collection_name]
        query_embedding = self.embeddings.embed_query(query)

        # Adjust parameters for different collection types
        if collection_name == "summary_chunks":
            k = rag_settings.SUMMARY_TOP_K
            threshold = 0.85
        else:
            threshold = 0.4

        # Step 1: Query the vector store
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["distances", "documents", "metadatas"],
            where=filter_dict if filter_dict else None 
        )

        documents = []

        # Step 2: Check and iterate through results
        if results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0]

            for i, distance in enumerate(distances):
                similarity = 1 - distance  # convert distance to similarity
                metadata = metadatas[i] if i < len(metadatas) else {}

                # Step 3: Manual post-filtering if backend doesn't support `where`
                if filter_dict:
                    match = all(metadata.get(k) == v for k, v in filter_dict.items())
                    if not match:
                        continue

                # Step 4: Add if above threshold
                if similarity >= threshold:
                    documents.append(
                        LCDocument(
                            page_content=docs[i],
                            metadata=metadata
                        )
                    )

        return documents


    def get_document_chunks(self, query: str, document_hash: str, k: int = 6) -> List[LCDocument]:
        collection = self.collections["book_chunks"]
        query_embedding = self.embeddings.embed_query(query)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where={"document_hash": document_hash}
        )
        return results["documents"]

    def get_all_processed_docs(self) -> Dict[Any, Any]:
        return {hash: doc_name['filename'] for (hash, doc_name) in self.processed_documents.items()}
