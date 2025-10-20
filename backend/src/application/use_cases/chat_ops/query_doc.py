from datetime import datetime
from typing import Any, Dict

from backend.src.application.interfaces.document_repository import \
    IVectorStoreRepository
from backend.src.domain.entities.query import Query


class QueryDocumentsUseCase:
    """Use case for querying documents"""
    
    def __init__(self, vector_store: IVectorStoreRepository):
        self._vector_store = vector_store
    
    def execute(self, query: Query) -> Dict[str, Any]:
        """
        Execute the query use case
        
        Returns:
            Dict with query context for LLM processing
        """
        start_time = datetime.now()
        
        # Enhance prompt with user context
        enhanced_prompt = self._enhance_prompt(query)
        
        # Retrieve relevant chunks
        similar_chunks = self._vector_store.search_similar(
            enhanced_prompt, 
            k=query.k
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "enhanced_prompt": enhanced_prompt,
            "relevant_chunks": similar_chunks,
            "original_query": query,
            "processing_time": processing_time
        }
    
    def _enhance_prompt(self, query: Query) -> str:
        """Enhance prompt with user profile context"""
        # not implemented
        enhanced = query.prompt
        
        return enhanced