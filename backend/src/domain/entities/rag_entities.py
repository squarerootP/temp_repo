from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class Chunk:
    id: str
    text: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Document:
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    hash: Optional[str] = None
    chunks: List[Chunk] = field(default_factory=list)


@dataclass
class Query:
    id: str
    text: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None


@dataclass
class Response:
    id: str
    answer: str
    source_chunks: List[str] = field(default_factory=list)
    query_id: str = ""
    confidence: Optional[float] = None


@dataclass
class VectorEmbedding:
    id: str
    vector: List[float]
    text_id: str
    model: str
@dataclass
class DocumentChunk:
    id: str
    page_content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    