import gc
import hashlib
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from config_optimized import Config
from embeddings_service_optimized import create_embeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentService:
    def __init__(self, persist_directory: str = "rag/vectorstore"):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""],
            keep_separator=True
        )
        self.embeddings = None
        self.vectorstore = None
        self.persist_directory = persist_directory
        self.metadata_file = os.path.join(persist_directory, "document_metadata.json")
        # Track the most recently uploaded document for query scoping
        self.current_document_hash: Optional[str] = None
        
        # Load processed documents from metadata
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
        """Initialize embeddings once with retry logic"""
        if self.embeddings is None:
            from tenacity import retry, stop_after_attempt, wait_exponential
            
            @retry(
                stop=stop_after_attempt(Config.MAX_RETRIES),
                wait=wait_exponential(multiplier=1, min=Config.RETRY_MIN_WAIT, max=Config.RETRY_MAX_WAIT)
            )
            def create_with_retry():
                return create_embeddings()
            
            try:
                self.embeddings = create_with_retry()
                print("✓ Embeddings initialized successfully")
            except Exception as e:
                raise Exception(f"Failed to initialize embeddings after retries: {str(e)}")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file content"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def add_documents(self, pdf_path: str) -> Dict[str, Any]:
        """Add documents from PDF with deduplication"""
        # Validate file exists
        if not os.path.isfile(pdf_path):
            raise FileNotFoundError(f"File not found: {pdf_path}")
        
        # Calculate file hash for duplicate detection
        try:
            file_hash = self._calculate_file_hash(pdf_path)
        except Exception as e:
            raise Exception(f"Failed to calculate file hash: {str(e)}")
        
        # Check for duplicates
        if file_hash in self.processed_documents:
            existing = self.processed_documents[file_hash]
            print(f"   ⚠️  Document already processed (hash: {file_hash[:8]}...)")
            # Ensure subsequent retrievals are scoped to this document
            self.current_document_hash = file_hash
            return {
                "status": "duplicate",
                "count": 0,
                "message": f"Document already exists: {existing['filename']}",
                "document_hash": file_hash,
                "metadata": existing
            }
        
        try:
            self._initialize_embeddings()
            
            print(f"   📄 Loading PDF: {os.path.basename(pdf_path)}")
            
            # Use PyPDFLoader for better text extraction
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            
            if not documents:
                raise ValueError("No content extracted from PDF")
            
            # Split documents
            print(f"   ✂️  Splitting into chunks...")
            splits = self.text_splitter.split_documents(documents)
            
            if not splits:
                raise ValueError("No text chunks created from document")
            
            # Add metadata to splits
            for i, split in enumerate(splits):
                split.metadata.update({
                    "document_hash": file_hash,
                    "chunk_id": f"{file_hash[:8]}_chunk_{i}",
                    "source_file": os.path.basename(pdf_path),
                    "chunk_index": i,
                    "total_chunks": len(splits)
                })
            
            # Process in batches to save memory
            BATCH_SIZE = Config.BATCH_SIZE
            print(f"   🔄 Processing {len(splits)} chunks in batches of {BATCH_SIZE}...")
            
            if self.vectorstore is None:
                # Create new vectorstore with first batch and explicit IDs
                first_batch = splits[:BATCH_SIZE]
                first_batch_ids = [doc.metadata["chunk_id"] for doc in first_batch]
                self.vectorstore = Chroma.from_documents(
                    documents=first_batch,
                    embedding=self.embeddings,
                    persist_directory=self.persist_directory,
                    collection_metadata={"hnsw:space": "cosine"},
                    ids=first_batch_ids
                )
                
                # Add remaining batches with explicit IDs
                for i in range(BATCH_SIZE, len(splits), BATCH_SIZE):
                    batch = splits[i:i + BATCH_SIZE]
                    batch_ids = [doc.metadata["chunk_id"] for doc in batch]
                    self.vectorstore.add_documents(batch, ids=batch_ids)
                gc.collect()
            else:
                # Add to existing vectorstore in batches with explicit IDs
                for i in range(0, len(splits), BATCH_SIZE):
                    batch = splits[i:i + BATCH_SIZE]
                    batch_ids = [doc.metadata["chunk_id"] for doc in batch]
                    self.vectorstore.add_documents(batch, ids=batch_ids)
                    gc.collect()
            
            # Store document metadata
            self.processed_documents[file_hash] = {
                "filename": os.path.basename(pdf_path),
                "upload_time": datetime.now().isoformat(),
                "chunk_count": len(splits),
                "page_count": len(documents),
                "file_size": os.path.getsize(pdf_path),
                "chunk_ids": [split.metadata["chunk_id"] for split in splits]
            }
            
            # Make this document the current scope for retrieval
            self.current_document_hash = file_hash

            # Save metadata
            self._save_metadata()
            
            print(f"   ✅ Processed {len(splits)} chunks from {len(documents)} pages")
            
            # Force garbage collection
            gc.collect()
            
            return {
                "status": "success",
                "count": len(documents),
                "message": f"Successfully processed {len(documents)} pages into {len(splits)} chunks",
                "document_hash": file_hash,
                "metadata": self.processed_documents[file_hash]
            }
        
        except Exception as e:
            raise Exception(f"Failed to process document: {str(e)}")
    
    def delete_document(self, document_hash: str) -> bool:
        """Delete a document and its chunks from vectorstore"""
        if document_hash not in self.processed_documents:
            return False
        
        try:
            metadata = self.processed_documents[document_hash]
            chunk_ids = metadata.get("chunk_ids", [])
            
            if chunk_ids and self.vectorstore:
                # Delete chunks from vectorstore
                self.vectorstore._collection.delete(ids=chunk_ids)
            
            # Remove from metadata
            del self.processed_documents[document_hash]
            self._save_metadata()

            # If the current scoped document is deleted, clear it
            if self.current_document_hash == document_hash:
                self.current_document_hash = None
            
            print(f"✓ Deleted document: {metadata['filename']}")
            return True
        except Exception as e:
            print(f"✗ Failed to delete document: {e}")
            return False
    
    def get_retriever(self, k: int = 4, document_hash: Optional[str] = None):
        """Get retriever scoped to the current or specified document"""
        if not self.vectorstore:
            raise ValueError("No documents loaded")
        selected_hash = document_hash or self.current_document_hash
        search_kwargs: Dict[str, Any] = {"k": k}
        if selected_hash:
            # Restrict search to the specified/current document
            search_kwargs["filter"] = {"document_hash": selected_hash}
        return self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs=search_kwargs
        )
    
    def get_processed_documents_info(self) -> Dict[str, Any]:
        """Get information about processed documents"""
        total_chunks = 0
        if self.vectorstore and hasattr(self.vectorstore, '_collection'):
            total_chunks = self.vectorstore._collection.count()
        
        return {
            "processed_count": len(self.processed_documents),
            "document_hashes": list(self.processed_documents.keys()),
            "total_chunks": total_chunks,
            "documents": [
                {
                    "hash": hash[:8] + "...",
                    "filename": meta["filename"],
                    "chunks": meta["chunk_count"],
                    "uploaded": meta["upload_time"]
                }
                for hash, meta in self.processed_documents.items()
            ]
        }
