from datetime import datetime
from uuid import uuid4

from backend.src.application.interfaces.rag_interfaces.chat_session_repository import \
    IChatSessionRepository
from backend.src.application.interfaces.rag_interfaces.rag_repository import \
    IRAGRepository
from backend.src.domain.entities.rag_entities.chat_history import (ChatMessage,
                                                                   ChatSession,
                                                                   MessageRole)
from backend.src.domain.exceptions.chat_exceptions import ChatHistoryNotFound
from backend.src.presentation.schemas.rag_schemas.chat_schema import \
    ChatMessageResponse


class ChatWithPriorDocuments:
    """
    Use case: Manages the full RAG pipeline with context awareness.
    Integrates chat history, context summarization, and query processing.
    """
    
    def __init__(
        self, 
        rag_repo: IRAGRepository,
        chat_repo: IChatSessionRepository
    ):
        self.rag_repo = rag_repo
        self.chat_repo = chat_repo
        # self.rag_orchestrator = RAGOrchestrator(rag_repo)
    
    def generate_response(
        self, 
        user_id: int, 
        session_id: str, 
        query: str
        ):

        # Step 1: Get or create session
        chat_session = self._get_or_create_session(user_id, session_id)
        
        # Step 2: Get the history and trim by the last 10 msgs
        history_msg = chat_session.messages[-10:]
        
        # Step 2.5: Format  history for summarization
        formatted_history = [{"role": msg.role.value, "content": msg.content} 
                                for msg in history_msg]

        # Step 2.6: Summarize history
        summarized_history = self.rag_repo.summarize_history(formatted_history)
        print("###Summarized history: ")
        print(summarized_history)
        print("###END summarization")
        
        # Step 3: Add user message to session
        user_msg = ChatMessage(content=query, role=MessageRole.USER, session_id=session_id)
        self.chat_repo.add_message_to_session(session_id, user_msg)
        # Step 4: Revise query with context
        revised_query = self.rag_repo.revise_query_with_context(query, summarized_history)
        print("### ReviseQuery:")
        print(revised_query)
        print("### End ReviseQuery")
        # Step 5: Get response from RAG system
        response = self.rag_repo.answer_query(
            session_id=session_id,
            user_query=revised_query,
        )
        final_response = response or "I couldn't generate a response."
        
        # Step 6: Add assistant message to session
        ai_msg = ChatMessage(content=final_response, role=MessageRole.ASSISTANT, session_id=session_id)
        self.chat_repo.add_message_to_session(session_id=session_id, message=ai_msg)
        
        # Step 6: Return structured response
        return ChatMessageResponse(
            content=ai_msg.content,
            role=ai_msg.role.value, #type: ignore
            timestamp=ai_msg.timestamp
        )
    
    def _get_or_create_session(self, user_id: int, session_id: str) -> ChatSession:
        """Get an existing session or create a new one if it doesn't exist."""
        try:
            # Try to get the session
            session = self.chat_repo.get_session_by_id(session_id)
            if session:
                print("Session found")
                print("All messages so far:")
                msgs = session.messages[-5:]
                for msg in msgs:
                    print(f"{msg.role} : {msg.content}")
                return session
        except ChatHistoryNotFound:
            # Session not found, create a new one
            pass
        
        # Create a new session
        new_session = ChatSession(
            session_id=session_id,
            messages=[],
            user_id=user_id
        )
        
        return self.chat_repo.create_session(new_session)