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
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Document:
    """A source document with its content and associated chunks."""
    id: str
    title: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    hash: Optional[str] = None
    chunks: List[DocumentChunk] = field(default_factory=list)
    uploaded_at: datetime = field(default_factory=datetime.now)
    user_id: Optional[int] = None