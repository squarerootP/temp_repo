import hashlib
import json
import os
from typing import Any, Dict, List, Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document
from sqlalchemy.orm import Session

from backend.src.application.interfaces.rag_interfaces.document_repository import (
    IDocumentRepository, IVectorStoreRepository)
from backend.src.domain.entities.rag_entities.document import (Document,
                                                               DocumentChunk)
from backend.src.infrastructure.adapters.mappers.rag_mappers.document_mapper import \
    DocumentMapper
from backend.src.infrastructure.adapters.rag.embedders.google_genai import \
    create_embeddings
from backend.src.infrastructure.persistence.models.rag_models import \
    DocumentModel
from logs.log_config import setup_logger

doc_logger = setup_logger("document_repo")

CHROMA_PERSIST_DIR = "./chroma_db"


class DocumentRepositoryImpl(IDocumentRepository):
    """Handles storing, loading, and chunking of documents, synced with vector store."""

    def __init__(self, db: Session, vector_repo: IVectorStoreRepository):
        self.db = db
        self.vector_repo = vector_repo
        self.text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=512,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""],
            keep_separator=True,
        )
        self.embeddings = None
        self.vectorstrore = None
        self.persist_directory = CHROMA_PERSIST_DIR
        self.metadata_file = os.path.join(self.persist_directory, "document_metadata.json")
        self.current_document_hash: Optional[str] = None
        
        self.processed_documents: Dict[str, Dict[str, Any]] = {}
        self._load_metadata()
        self._load_vectorstore()

    # ------------------- DATABASE OPERATIONS -------------------

    def get_all_documents(self) -> List[Document]:
        db_docs = self.db.query(DocumentModel).all()
        return [DocumentMapper.to_entity(doc) for doc in db_docs]

    def save_document(self, document: Document) -> Document:
        """Persist a document entity to the database."""
        db_doc = DocumentMapper.to_model(document)
        self.db.add(db_doc)
        self.db.commit()
        self.db.refresh(db_doc)
        return DocumentMapper.to_entity(db_doc)

    def get_document_by_hash(self, content_hash: str) -> Optional[Document]:
        """Retrieve a document by its hash (used to detect duplicates)."""
        db_doc = (
            self.db.query(DocumentModel)
            .filter(DocumentModel.hash == content_hash)
            .first()
        )
        
        if not db_doc:
            doc_logger.info(f"No document found with hash {content_hash}")
            
        return DocumentMapper.to_entity(db_doc) if db_doc else None

    def delete_document(self, document_hash: str) -> bool:
        """Delete a document by its hash."""
        db_doc = (
            self.db.query(DocumentModel)
            .filter(DocumentModel.hash == document_hash)
            .first()
        )
        if not db_doc:
            doc_logger.info(f"No document found with hash {document_hash} to delete")
            return False
        
        self.db.delete(db_doc)
        self.db.commit()
        
        doc_logger.info(f"Deleted document with hash {document_hash}")
        
        return True

    def document_exists(self, content_hash: str) -> bool:
        """Check if a document already exists (by hash)."""
        return (
            self.db.query(DocumentModel)
            .filter(DocumentModel.hash == content_hash)
            .first()
            is not None
        )

    # ------------------- DOCUMENT PROCESSING -------------------

    def hash_document(self, document: Document) -> str:
        """Generate a SHA256 hash of the document content."""
        content_hash = hashlib.sha256(document.content.encode("utf-8")).hexdigest()
        if not content_hash:
            raise ValueError("failed to hash")
        document.hash = content_hash
        
        return content_hash

    def process_document(self, file_path: str) -> Document:
        """Load, hash, chunk, and prepare a document for storage."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Create a document entity
        document = Document(
            id=os.path.basename(file_path),
            title=os.path.basename(file_path),
            content=content,
        )
        document.hash = self.hash_document(document)
        document.chunks = self.chunk_document(document)

        return document

    def chunk_document(self, document: Document) -> List[DocumentChunk]:
        """Split the document into smaller chunks."""
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=512, chunk_overlap=50
        )
        splits = text_splitter.split_text(document.content)

        chunks = [
            DocumentChunk(
                id=f"{document.id}_{i}",
                page_content=chunk,
                document_id=document.id,
                metadata={"source_document": document.title})            
            for i, chunk in enumerate(splits)
        ]
        return chunks

    # ------------------- VECTOR STORE SYNC -------------------
    def _load_metadata(self):
        """Load document metadata from JSON file"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    self.processed_documents = json.load(f)
                print(f"✓ Loaded metadata for {len(self.processed_documents)} documents")
            except Exception as e:
                print(f"⚠️  Failed to load metadata: {e}")
                self.processed_documents = {}
                
    def _save_metadata(self):
        """Save document metadata to JSON file"""
        try:
            os.makedirs(self.persist_directory, exist_ok=True)
            with open(self.metadata_file, 'w') as f:
                json.dump(self.processed_documents, f, indent=2, default=str)
        except Exception as e:
            print(f"⚠️  Failed to save metadata: {e}")

    def _load_vectorstore(self):
        """Load vectorstore from disk if exists"""
        if os.path.exists(self.persist_directory):
            try:
                self._initialize_embeddings()
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings,
                    collection_metadata={"hnsw:space": "cosine"}
                )
                print(f"✓ Loaded vectorstore with {self.vectorstore._collection.count()} chunks")
            except Exception as e:
                print(f"⚠️  Failed to load vectorstore: {e}")
                self.vectorstore = None
                
    def _initialize_embeddings(self):
        return create_embeddings()


