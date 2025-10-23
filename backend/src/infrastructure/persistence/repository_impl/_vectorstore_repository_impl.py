import gc
import hashlib
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tenacity import retry, stop_after_attempt, wait_exponential

from backend.src.application.interfaces.a_document_repository import \
    IDocumentRepository
from backend.src.domain.entities._document import Document, DocumentChunk, VectorEmbedding
from backend.src.infrastructure.adapters.rag.embedders.google_genai import \
    create_embeddings
from backend.src.infrastructure.rag.config_optimized import Config
from backend.src.application.interfaces.a_embedding_repository import IEmbeddingRepository

class ChromaVectorStoreRepositoryImpl(IEmbeddingRepository):
    def __init__(self, persist_directory: str = "rag/vectorstore"):
        self.persist_directory = persist_directory
        self.metadata_file = os.path.join(persist_directory, "document_metadata.json")

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""],
            keep_separator=True
        )

        self.embeddings = None
        self.vectorstore = None
        self.current_document_hash: Optional[str] = None
        self.processed_documents: Dict[str, Dict[str, Any]] = {}

        self._load_metadata()
        self._load_vectorstore()

    # ---------------------------
    # Internal Helpers
    # ---------------------------

    def _load_metadata(self):
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, "r") as f:
                    self.processed_documents = json.load(f)
            except Exception:
                self.processed_documents = {}

    def _save_metadata(self):
        os.makedirs(self.persist_directory, exist_ok=True)
        with open(self.metadata_file, "w") as f:
            json.dump(self.processed_documents, f, indent=2, default=str)

    def _initialize_embeddings(self):
        if self.embeddings is None:
            @retry(
                stop=stop_after_attempt(Config.MAX_RETRIES),
                wait=wait_exponential(multiplier=1, min=Config.RETRY_MIN_WAIT, max=Config.RETRY_MAX_WAIT)
            )
            def create_with_retry():
                return create_embeddings()

            self.embeddings = create_with_retry()

    def _load_vectorstore(self):
        if os.path.exists(self.persist_directory):
            try:
                self._initialize_embeddings()
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings,
                    collection_metadata={"hnsw:space": "cosine"}
                )
            except Exception:
                self.vectorstore = None

    def _calculate_file_hash(self, file_path: str) -> str:
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    # ---------------------------
    # Repository Methods
    # ---------------------------

    def add_document(self, pdf_path: str) -> Dict[str, Any]:
        if not os.path.isfile(pdf_path):
            raise FileNotFoundError(f"File not found: {pdf_path}")

        file_hash = self._calculate_file_hash(pdf_path)

        # Duplicate check
        if file_hash in self.processed_documents:
            self.current_document_hash = file_hash
            return {"status": "duplicate", "hash": file_hash}

        self._initialize_embeddings()
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        splits = self.text_splitter.split_documents(documents)

        for i, split in enumerate(splits):
            split.metadata.update({
                "document_hash": file_hash,
                "chunk_id": f"{file_hash[:8]}_chunk_{i}",
                "source_file": os.path.basename(pdf_path),
                "chunk_index": i,
                "total_chunks": len(splits)
            })

        BATCH_SIZE = Config.BATCH_SIZE
        if self.vectorstore is None:
            first_batch = splits[:BATCH_SIZE]
            first_ids = [doc.metadata["chunk_id"] for doc in first_batch]
            self.vectorstore = Chroma.from_documents(
                documents=first_batch,
                embedding=self.embeddings,
                persist_directory=self.persist_directory,
                collection_metadata={"hnsw:space": "cosine"},
                ids=first_ids
            )

        for i in range(BATCH_SIZE, len(splits), BATCH_SIZE):
            batch = splits[i:i + BATCH_SIZE]
            ids = [doc.metadata["chunk_id"] for doc in batch]
            self.vectorstore.add_documents(batch, ids=ids)
            gc.collect()

        self.processed_documents[file_hash] = {
            "filename": os.path.basename(pdf_path),
            "upload_time": datetime.now().isoformat(),
            "chunk_count": len(splits),
            "file_size": os.path.getsize(pdf_path),
            "chunk_ids": [d.metadata["chunk_id"] for d in splits]
        }
        self._save_metadata()
        self.current_document_hash = file_hash

        return {"status": "success", "hash": file_hash, "chunks": len(splits)}

    def delete_document(self, document_hash: str) -> bool:
        if document_hash not in self.processed_documents:
            return False
        try:
            chunk_ids = self.processed_documents[document_hash].get("chunk_ids", [])
            if chunk_ids and self.vectorstore:
                self.vectorstore._collection.delete(ids=chunk_ids)
            del self.processed_documents[document_hash]
            self._save_metadata()
            if self.current_document_hash == document_hash:
                self.current_document_hash = None
            return True
        except Exception:
            return False

    def get_retriever(self, k: int = 4, document_hash: Optional[str] = None):
        if not self.vectorstore:
            raise ValueError("Vectorstore not initialized")
        selected_hash = document_hash or self.current_document_hash
        kwargs = {"k": k}
        if selected_hash:
            kwargs["filter"] = {"document_hash": selected_hash} # type: ignore
        return self.vectorstore.as_retriever(search_type="similarity", search_kwargs=kwargs)


    def save_embedding(self, document: Document, embedding: VectorEmbedding) -> None:
        return super().save_embedding(document, embedding)
    def get_embedding(self, doc_hash: str) -> VectorEmbedding | None:
        return super().get_embedding(doc_hash)
    
    def generate_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
        return super().generate_embedding(text, model)