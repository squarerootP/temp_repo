import asyncio
import hashlib
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from rag.config_optimized import Config
from rag.monitoring_service import monitor
from rag.rag_optimized import RAG

# Validate config on startup
try:
    Config.validate()
except Exception as e:
    print(f"❌ Configuration error: {e}")
    exit(1)

app = FastAPI(
    title="RAG API - Optimized", 
    description="Retrieval-Augmented Generation API with Caching and Performance Monitoring",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
rag_system = RAG()
executor = ThreadPoolExecutor(max_workers=Config.MAX_CONCURRENT_REQUESTS)

# Pydantic Models
class UserProfile(BaseModel):
    user_id: int
    preferences: Optional[Dict[str, Any]] = {}
    context: Optional[str] = None

class QueryRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="The user's question")
    user_profile: Optional[UserProfile] = None
    k: Optional[int] = Field(6, ge=1, le=20, description="Number of chunks to retrieve")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.0, description="LLM temperature")

class DocumentMetadata(BaseModel):
    filename: str
    document_hash: str
    upload_time: datetime
    chunk_count: int
    status: str
    
class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    user_id: Optional[int] = None
    processing_time: float
    timestamp: datetime
    cached: bool = False

class DocumentUploadResponse(BaseModel):
    message: str
    document_metadata: DocumentMetadata
    processing_time: float

# Helper Functions
def calculate_document_hash(content: bytes) -> str:
    """Calculate SHA-256 hash"""
    return hashlib.sha256(content).hexdigest()

def enhance_prompt_with_user_profile(prompt: str, user_profile: Optional[UserProfile]) -> str:
    """Enhance prompt with user context"""
    if not user_profile:
        return prompt
    
    enhanced = prompt
    
    if user_profile.context:
        enhanced = f"Context: {user_profile.context}\n\nQuestion: {enhanced}"
    
    if user_profile.preferences:
        prefs = ", ".join([f"{k}: {v}" for k, v in user_profile.preferences.items()])
        enhanced = f"User preferences: {prefs}\n\n{enhanced}"
    
    return enhanced

async def process_document_async(file_content: bytes, filename: str) -> DocumentUploadResponse:
    """Process document asynchronously"""
    loop = asyncio.get_event_loop()
    
    def process_sync():
        start_time = datetime.now()
        tmp_file_path = None
        
        try:
            # Save temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(file_content)
                tmp_file_path = tmp_file.name
            
            # Process document
            result = rag_system.load_documents(tmp_file_path)
            doc_hash = calculate_document_hash(file_content)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return DocumentUploadResponse(
                message=result.get("message", "Document processed successfully"),
                document_metadata=DocumentMetadata(
                    filename=filename,
                    document_hash=doc_hash,
                    upload_time=start_time,
                    chunk_count=result.get("metadata", {}).get("chunk_count", 0),
                    status=result.get("status", "success")
                ),
                processing_time=processing_time
            )
        
        except Exception as e:
            raise Exception(f"Document processing failed: {str(e)}")
        finally:
            if tmp_file_path and os.path.exists(tmp_file_path):
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
    
    return await loop.run_in_executor(executor, process_sync)

# API Endpoints
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "RAG API - Optimized Version",
        "version": "2.0.0",
        "status": "healthy",
        "config": Config.get_summary()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    system_info = rag_system.get_system_info()
    return {
        "status": "healthy",
        "initialized": system_info["initialized"],
        "documents_loaded": system_info["documents"]["processed_count"],
        "total_chunks": system_info["documents"]["total_chunks"],
        "cache_enabled": Config.ENABLE_QUERY_CACHE,
        "timestamp": datetime.now()
    }

@app.get("/system-info")
async def get_system_info():
    """Get detailed system information"""
    return rag_system.get_system_info()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    monitor.start_monitoring(interval=30)
    print("✓ Application started successfully")
    print(f"  - Cache enabled: {Config.ENABLE_QUERY_CACHE}")
    print(f"  - Max file size: {Config.MAX_FILE_SIZE / (1024*1024):.1f}MB")
    print(f"  - Chunk size: {Config.CHUNK_SIZE}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    monitor.stop_monitoring()
    executor.shutdown(wait=True)
    print("✓ Application shutdown complete")

@app.get("/metrics")
async def get_performance_metrics():
    """Get performance metrics"""
    return monitor.get_performance_report()

@app.post("/optimize-memory")
async def optimize_memory():
    """Force memory optimization"""
    return monitor.optimize_memory(force=True)

@app.post("/clear-cache")
async def clear_cache():
    """Clear query cache"""
    if rag_system.query_cache:
        rag_system.clear_cache()
        return {"status": "success", "message": "Query cache cleared"}
    return {"status": "info", "message": "Cache not enabled"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a PDF document"""
    # Validate filename
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    # Validate file extension
    if not Config.validate_file_extension(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed: {', '.join(Config.ALLOWED_EXTENSIONS)}"
        )
    
    # Read and validate file content
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded")
    
    if not Config.validate_file_size(len(content)):
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {Config.MAX_FILE_SIZE / (1024*1024):.1f}MB"
        )
    
    try:
        # Process document
        response = await process_document_async(content, file.filename)
        return response
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(e)}"
        )

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query the RAG system with full response details"""
    # Check if documents are loaded
    if not rag_system.is_initialized:
        raise HTTPException(
            status_code=400,
            detail="No documents loaded. Please upload a PDF document first."
        )
    
    try:
        start_time = datetime.now()
        loop = asyncio.get_event_loop()
        
        # Enhance prompt with user profile
        enhanced_prompt = enhance_prompt_with_user_profile(
            request.prompt,
            request.user_profile
        )
        
        # Query the system
        response = await loop.run_in_executor(
            executor,
            lambda: rag_system.query(enhanced_prompt, k=request.k or 6)
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Format sources
        sources = []
        for i, doc in enumerate(response.get('context', []), 1):
            sources.append({
                "source_id": i,
                "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                "metadata": doc.metadata
            })
        
        return QueryResponse(
            answer=response.get('answer', ''),
            sources=sources,
            user_id=request.user_profile.user_id if request.user_profile else None,
            processing_time=processing_time,
            timestamp=datetime.now(),
            cached=response.get('cached', False)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )

@app.post("/chat")
async def chat_with_context(request: QueryRequest):
    """Simplified chat endpoint for easy integration"""
    try:
        query_response = await query_documents(request)
        
        # Return simplified JSON
        return {
            "response": query_response.answer,
            "sources": len(query_response.sources),
            "user_id": query_response.user_id,
            "timestamp": query_response.timestamp.isoformat(),
            "processing_time_ms": round(query_response.processing_time * 1000),
            "cached": query_response.cached
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/status")
async def get_documents_status():
    """Get information about processed documents"""
    try:
        info = rag_system.document_service.get_processed_documents_info()
        return {
            "processed_documents": info["processed_count"],
            "total_chunks": info["total_chunks"],
            "documents": info["documents"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{document_hash}")
async def delete_document(document_hash: str):
    """Delete a specific document"""
    try:
        success = rag_system.document_service.delete_document(document_hash)
        if success:
            # Clear cache when documents change
            if rag_system.query_cache:
                rag_system.clear_cache()
            return {"status": "success", "message": f"Document {document_hash[:8]}... deleted"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
