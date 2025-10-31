import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.src.domain.entities.library_entities.book import Book


@dataclass
class Document:
    """A source document with its content and associated chunks."""

    book_isbn: str
    title: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    hash: Optional[str] = None
    book: Optional[Book] = None
