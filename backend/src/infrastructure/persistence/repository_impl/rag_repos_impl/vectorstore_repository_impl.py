import gc
import hashlib
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import chardet
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.src.application.interfaces.rag_interfaces.vectorstore_repo import \
    IVectorStoreRepository
from backend.src.domain.entities.rag_entities.document import (Document,
                                                               DocumentChunk)
from backend.src.infrastructure.adapters.document_hasher import DocumentHasher
from backend.src.infrastructure.config.settings import rag_settings
from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.tools.doc_retriever_tool import \
    get_embedding_function
from backend.src.infrastructure.config.settings import rag_settings
from langchain_core.documents import Document as LCDocument

TEXT_FILES_DIR = rag_settings.TEXT_FILES_DIR
CHROMA_PERSIST_DIR = rag_settings.CHROMA_PERSIST_DIR
TEXT_FILES = [
    os.path.join(TEXT_FILES_DIR, f)
    for f in os.listdir(TEXT_FILES_DIR) if os.path.isfile(os.path.join(TEXT_FILES_DIR, f)) and f.lower().endswith('.txt')
]
print("=== Text files to process:", TEXT_FILES)

class ChromaVectorStoreRepositoryImpl(IVectorStoreRepository):
    """Concrete vector store repository using Chroma and Google embeddings."""

    def __init__(self, persist_directory: str = rag_settings.CHROMA_PERSIST_DIR):
        self.persist_directory = persist_directory
        self.metadata_file = os.path.join(persist_directory, "document_metadata.json")

        self.text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=rag_settings.CHUNK_SIZE,
            chunk_overlap=rag_settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""],
            keep_separator=True,
        )

        self.embeddings = None
        self.vectorstore = None
        self.current_document_hash: Optional[str] = None
        self.processed_documents: Dict[str, Dict[str, Any]] = {}

        self._load_metadata()
        self._load_vectorstore()


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
        """Load vectorstore from disk if exists or create new one from documents"""
        if os.path.exists(self.persist_directory):
            try:
                self.embeddings = self._initialize_embeddings()
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings,
                    collection_metadata={"hnsw:space": "cosine"}
                )
                print(f"✓ Loaded vectorstore with {self.vectorstore._collection.count()} chunks")
            except Exception as e:
                print(f"⚠️  Failed to load vectorstore: {e}")
                self.vectorstore = None
        else:
            try:
                print("Creating new vectorstore...")
                self.embeddings = self._initialize_embeddings()
                
                # Process all documents first
                all_chunks = []
                all_chunk_ids = []
                
                for text_file_path in TEXT_FILES:
                    file_hash = DocumentHasher.hash_file(text_file_path)
                    if file_hash not in self.processed_documents:
                        print(f"Processing document: {text_file_path}")
                        document = self.process_document(text_file_path, file_hash)
                        # Note: process_document already adds chunks to processed_documents
                        
                # Create vectorstore with all documents at once
                if self.processed_documents:
                    print("Initializing vectorstore with processed documents...")
                    self.vectorstore = Chroma(
                        persist_directory=self.persist_directory,
                        embedding_function=self.embeddings,
                        collection_metadata={"hnsw:space": "cosine"}
                    )

                    print(f"✓ Created and persisted vectorstore with {self.vectorstore._collection.count()} chunks")
                else:
                    print("No documents to process")
                    
            except Exception as e:
                print(f"⚠️  Failed to create vectorstore: {e}")
                self.vectorstore = None
                raise

    def _initialize_embeddings(self):
        return get_embedding_function()

    
    # ==== CORE METHODS ====
    def process_document(self, file_path: str, hash: str) -> Document:
        """Load, hash, chunk, and prepare a document for storage."""

        try:
            # Read file
            with open(file_path, "rb") as file:
                raw_data = file.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding'] if result['encoding'] else 'utf-8'
            with open(file_path, "r", encoding=encoding) as file:
                content = file.read()
            # Load content
            documents = TextLoader(file_path, encoding="utf-8").load()
            # Chunking
            chunks = self.text_splitter.split_documents(documents)
            
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    "document_hash": hash,
                    "chunk_id": f"{hash[:8]}_chunk_{i}",
                    "source_file": os.path.basename(file_path),
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                })      

            if not self.vectorstore:
                self._initialize_embeddings()
                self.vectorstore = Chroma.from_documents(
                    documents=chunks,
                    embedding=self.embeddings,
                    persist_directory=self.persist_directory,
                    collection_metadata={"hnsw:space": "cosine"},
                    ids=[chunk.metadata["chunk_id"] for chunk in chunks]
                )
            
            self.processed_documents[hash] = {
                "filename": os.path.basename(file_path),
                "chunk_count": len(chunks),
                "chunk_ids": [chunk.metadata["chunk_id"] for chunk in chunks]
            }
            
            self._save_metadata()
            
            document_entity = Document(
                id=hash,
                title=os.path.basename(file_path),
                content=content,
                hash=hash,)
            
            return document_entity
        except Exception as e:
            raise RuntimeError(f"Failed to process document {file_path}: {e}")

    def add_chunks_to_vectorstore(self, chunks: List[Any], chunk_ids: List[str]):
        """Add new chunks to existing vectorstore"""
        if not self.vectorstore:
            self._initialize_embeddings()
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=self.persist_directory,
                collection_metadata={"hnsw:space": "cosine"},
                ids=chunk_ids
            )
        else:
            self.vectorstore.add_documents(
                documents=chunks,
                ids=chunk_ids
            )




    def delete_document_chunks(self, document_hash: str) -> bool:
        """Delete all chunks for a document"""
        if document_hash not in self.processed_documents:
            return False
        
        chunk_ids = self.processed_documents[document_hash]["chunk_ids"]
        self.vectorstore._collection.delete(ids=chunk_ids) #type: ignore
        del self.processed_documents[document_hash]
        self._save_metadata()
        return True

    def get_similar_chunks(self, query: str, k: int = 4) -> List[LCDocument]:
        """Get similar chunks for a query"""
        if not self.vectorstore:
            return []
            
        try:
            results = self.vectorstore.similarity_search(query, k=k)
            
            documents = results
            print("+++++Hello")
            print(document.page_content for document in documents)
            
            return documents
            
        except Exception as e:
            print(f"Error in similarity search: {e}")
            return []
        
    def get_document_chunks(self, query: str, document_hash: str, k: int = 6) -> List[LCDocument]:
        """Get all chunks for a specific document"""
        if not self.vectorstore:
            return []
            
        try:
            # results = self.vectorstore.similarity_search(query, k=1000, filter={"document_hash": document_hash})
            
            return self.vectorstore.similarity_search(
                query, k=k, filter={"document_hash": document_hash}
            )
            
            
        except Exception as e:
            print(f"Error retrieving document chunks: {e}")
            return []
    
    def get_all_processed_docs(self) -> List[Any]:
        return list(self.processed_documents.keys())
