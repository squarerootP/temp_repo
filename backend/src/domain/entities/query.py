from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass

@dataclass
class Query:
    """Query entity - represents a user's question"""
    prompt: str
    k: int = 4
    temperature: float = 0.7
    timestamp: datetime = None #type: ignore
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if not self.prompt.strip():
            raise ValueError("Query prompt cannot be empty")
        if self.k <= 0:
            raise ValueError("k must be positive")
        if not 0 <= self.temperature <= 1:
            raise ValueError("Temperature must be between 0 and 1")

@dataclass
class QueryResult:
    """Result of a query operation"""
    answer: str
    sources: List[Dict[str, Any]]
    user_id: Optional[str]
    processing_time: float
    timestamp: datetime
    confidence_score: Optional[float] = None
    
    def __post_init__(self):
        if self.processing_time < 0:
            raise ValueError("Processing time cannot be negative")