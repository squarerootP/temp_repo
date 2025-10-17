from abc import ABC, abstractmethod
from typing import AsyncIterator


class RAGServiceInterface(ABC):
    """Abstraction for RAG chat services used by chat use-cases.

    Implementations may stream events and produce a final response.
    """

    @abstractmethod
    def stream_chat(self, user_input: str, thread_id: str) -> AsyncIterator[dict]:
        """Yield streaming events for a given user input within a thread.

        Implementations may be async generators; callers can `async for` over the result.
        """
        raise NotImplementedError

    @abstractmethod
    async def process_message(self, user_input: str, thread_id: str) -> str:
        """Return the final assistant response for a given user input."""
        raise NotImplementedError
