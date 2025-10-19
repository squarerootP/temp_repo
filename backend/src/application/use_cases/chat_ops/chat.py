from typing import AsyncIterator

from backend.src.application.interfaces.chat_repository import \
    RAGServiceInterface


class ChatInteraction:
    def __init__(self, rag_service: RAGServiceInterface):
        self.rag_service = rag_service
    
    async def execute(self, user_input: str, thread_id: str = "1") -> AsyncIterator[dict]:
        """Execute chat interaction use case"""
        async for event in self.rag_service.stream_chat(user_input, thread_id):
            yield event
    