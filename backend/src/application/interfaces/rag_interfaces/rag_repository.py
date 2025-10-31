from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IRAGRepository(ABC):
    @abstractmethod
    def initialize_graph(self) -> Any:
        """Initialize and return the RAG graph."""
        pass

    @abstractmethod
    def answer_query(self, user_query: str) -> str:
        """Run retrieval + generation + storage pipeline."""
        pass

    @abstractmethod
    def summarize_history(self, formatted_history: List[Dict[str, Any]]) -> str:
        """Summarize chat history for context.

        Args:
            history: A list of message dictionaries with 'role' and 'content' keys

        Returns:
            A concise summary of the conversation
        """
        pass

    @abstractmethod
    def revise_query_with_context(self, query: str, context: str) -> str:
        """Revise the user query by incorporating provided context.

        Args:
            query: The original user query
            context: The context to incorporate into the query

        Returns:
            The revised query string
        """
        pass

    @abstractmethod
    def answer_query_with_specific_document(
        self, session_id: str, user_query: str, document_hash: Optional[str]
    ) -> str:
        """Run retrieval + generation + storage pipeline with a specific document.

        Args:
            session_id: The chat session identifier
            user_query: The user's query
            document_hash: The hash of the specific document to use

        Returns:
            The generated response string
        """
        pass
