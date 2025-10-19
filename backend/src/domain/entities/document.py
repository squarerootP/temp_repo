from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Document:
    """Core document entity - represents a document in the system"""
    id: str
    filename: str
    content_hash: str
    upload_time: datetime
    chunk_count: int
    file_size: int
    metadata: dict
    
    def __post_init__(self):
        if self.chunk_count < 0:
            raise ValueError("Chunk count cannot be negative")
        if self.file_size <= 0:
            raise ValueError("File size must be positive")

@dataclass
class DocumentChunk:
    """Represents a chunk of a document"""
    chunk_id: str
    document_id: str
    content: str
    metadata: dict
    embedding: Optional[List[float]] = None
    
    def __post_init__(self):
        if not self.content.strip():
            raise ValueError("Chunk content cannot be empty")