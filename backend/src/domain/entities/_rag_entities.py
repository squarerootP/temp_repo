from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Query:
    id: str
    text: str
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class Response:
    id: str
    answer: str
    source_chunks: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    query_id: str = ""
    confidence: Optional[float] = None
    session_id: Optional[str] = None

