import hashlib
import time
from datetime import datetime
from typing import Any, Dict, Optional

from rag.config_optimized import Config
from rag.document_service_optimized import DocumentService
from rag.llm_service_optimized import LLMService


class QueryCache:
    """Simple in-memory cache with TTL"""
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
    
    def _get_cache_key(self, question: str, k: int) -> str:
        """Generate cache key from question and parameters"""
        combined = f"{question.lower().strip()}:{k}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get(self, question: str, k: int) -> Optional[Dict[str, Any]]:
        """Get cached response if exists and not expired"""
        key = self._get_cache_key(question, k)
        
        if key in self.cache:
            entry = self.cache[key]
            age = (datetime.now() - entry["timestamp"]).total_seconds()
            
            if age < self.ttl_seconds:
                print(f"   💾 Cache HIT (age: {age:.1f}s)")
                entry["response"]["cached"] = True
                return entry["response"]
            else:
                # Expired, remove it
                del self.cache[key]
                print(f"   ⏰ Cache EXPIRED (age: {age:.1f}s)")
        
        print("   🔍 Cache MISS")
        return None
    
    def set(self, question: str, k: int, response: Dict[str, Any]):
        """Cache a response"""
        key = self._get_cache_key(question, k)
        
        # Implement simple LRU eviction
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["timestamp"])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            "response": response,
            "timestamp": datetime.now()
        }
    
    def clear(self):
        """Clear all cached entries"""
        self.cache.clear()
        print("✓ Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds
        }

class RAG:
    def __init__(self):
        print("Initializing RAG system...")
        start_time = time.time()
        
        try:
            # Initialize document service
            self.document_service = DocumentService()
            self.llm_service = None  # Lazy initialization
            self.is_initialized = False
            
            # Initialize query cache
            self.query_cache = QueryCache(
                max_size=Config.CACHE_MAX_SIZE,
                ttl_seconds=Config.CACHE_TTL_SECONDS
            ) if Config.ENABLE_QUERY_CACHE else None
            
            init_time = time.time() - start_time
            print(f"✓ RAG system initialized in {init_time:.2f} seconds")
            print(f"  - Cache enabled: {Config.ENABLE_QUERY_CACHE}")
            
        except Exception as e:
            print(f"✗ Failed to initialize RAG system: {str(e)}")
            raise
    
    def _initialize_llm(self):
        """Lazy initialization of LLM service"""
        if self.llm_service is None:
            try:
                print("   🤖 Initializing LLM service...")
                start_time = time.time()
                self.llm_service = LLMService()
                init_time = time.time() - start_time
                print(f"   ✓ LLM service initialized in {init_time:.2f} seconds")
            except Exception as e:
                print(f"   ✗ Failed to initialize LLM service: {str(e)}")
                raise
    
    def load_documents(self, pdf_path: str) -> Dict[str, Any]:
        """Load documents and create vectorstore"""
        try:
            print(f"\n📚 Loading documents from: {pdf_path}")
            start_time = time.time()
            
            result = self.document_service.add_documents(pdf_path)
            
            # Only mark as initialized if we have documents
            if result["status"] == "success" or (
                result["status"] == "duplicate" and 
                self.document_service.get_processed_documents_info()["processed_count"] > 0
            ):
                self.is_initialized = True
            
            load_time = time.time() - start_time
            
            # Clear cache when documents are loaded (even duplicates)
            if self.query_cache:
                self.query_cache.clear()
                print("   💾 Cache cleared for fresh queries")
            
            print(f"✓ Completed in {load_time:.2f} seconds")
            return result
            
        except Exception as e:
            error_msg = f"Error loading documents: {str(e)}"
            print(f"✗ {error_msg}")
            raise Exception(error_msg)
    
    def query(self, question: str, k: int = 6) -> Dict[str, Any]:
        """Query the RAG system with caching"""
        if not self.is_initialized:
            raise ValueError("No documents loaded. Please load documents first.")
        
        # Check cache first
        if self.query_cache and Config.ENABLE_QUERY_CACHE:
            cached_response = self.query_cache.get(question, k)
            if cached_response:
                return cached_response
        
        try:
            print(f"\n❓ Processing query: {question[:50]}...")
            start_time = time.time()
            
            self._initialize_llm()
            retriever = self.document_service.get_retriever(k=k)
            response = self.llm_service.generate_response(question, retriever) #type: ignore
            
            query_time = time.time() - start_time
            print(f"✓ Query processed in {query_time:.2f} seconds")
            
            # Ensure response is a dictionary
            if isinstance(response, str):
                response = {
                    "answer": response,
                    "context": [],
                    "processing_time": query_time,
                    "cached": False
                }
            else:
                response["processing_time"] = query_time
                response["cached"] = False
            
            # Cache the response
            if self.query_cache and Config.ENABLE_QUERY_CACHE:
                self.query_cache.set(question, k, response)
            
            return response
            
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            print(f"✗ {error_msg}")
            raise Exception(error_msg)
    
    def clear_cache(self):
        """Clear query cache"""
        if self.query_cache:
            self.query_cache.clear()
    
    def clear_all_documents(self):
        """Clear all documents from vectorstore"""
        doc_info = self.document_service.get_processed_documents_info()
        if doc_info['processed_count'] > 0:
            for doc_hash in doc_info['document_hashes']:
                self.document_service.delete_document(doc_hash)
            self.is_initialized = False
            if self.query_cache:
                self.query_cache.clear()
            print("✓ All documents cleared")
            return True
        return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        doc_info = self.document_service.get_processed_documents_info()
        
        info = {
            "initialized": self.is_initialized,
            "documents": doc_info,
            "llm_initialized": self.llm_service is not None,
            "config": Config.get_summary()
        }
        
        if self.query_cache:
            info["cache"] = self.query_cache.get_stats()
        
        return info
