import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class DocumentChunk:
    """A wrapper used for retrieval/display; closely mirrors LangChain's Document."""
    id: str
    page_content: str
    document_id: str
    embedding_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VectorEmbedding:
    """Domain entity representing an embedding vector (stored in ChromaDB or similar)."""
    id: str 
    vector: List[float] = field(default_factory=list)
    chunk_id: Optional[str] = None 
    metadata: Dict[str, Any] = field(default_factory=dict)
    model: str = "unknown"
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Document:
    """A source document with its content and associated chunks."""
    id: str
    title: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    hash: Optional[str] = None
    chunks: List[DocumentChunk] = field(default_factory=list)
