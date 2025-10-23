from backend.src.application.interfaces._chat_session_repository import \
    IChatSessionRepository
from backend.src.application.interfaces._rag_repository import IRAGRepository
from backend.src.domain.entities._chat_history import (ChatMessage, ChatSession,
                                                      MessageRole)
from backend.src.domain.exceptions.chat_exceptions import ChatHistoryNotFound


class ChatWithSpecificDocument:
    """
    Use case: Use the document hash to find the document that the user wants to chat about.
    """
    
    def __init__(
        self, 
        rag_repo: IRAGRepository,
        chat_session_repo: IChatSessionRepository,
        hash: str
    ):
        self.rag_repo = rag_repo
        self.chat_session_repo = chat_session_repo
        self.hash = hash
    
    def generate_response(
        self, 
        user_id: int, 
        session_id: str, 
        query: str
        )   -> ChatMessage:

        # Step 1: Get or create session
        chat_session = self._get_or_create_session(user_id, session_id)
        
        # Step 2: Get the history
        history_msg = chat_session.messages
        
        # Step 2.5: Format and trim history for summarization
        formatted_history = [{"role": msg.role.value, "content": msg.content} 
                                for msg in history_msg]
        trimmed_history = formatted_history[-5:]
        
        # Step 2.6: Summarize history
        summarized_history = self.rag_repo.summarize_history(trimmed_history)
        
        # Step 3: Add user message to session
        user_msg = ChatMessage(content=query, role=MessageRole.USER, session_id=session_id)
        self.chat_session_repo.add_message_to_session(session_id, user_msg)
        
        # Step 4: Revise query with context
        revised_query = self.rag_repo.revise_query_with_context(query, summarized_history)
        
        # Step 5: Get response from RAG system
        response = self.rag_repo.answer_query_with_specific_document(
            session_id=session_id,
            user_query=revised_query,
            doc_hash = self.hash
        )
        final_response = response or "I couldn't generate a response."
        
        # Step 6: Add assistant message to session
        ai_msg = ChatMessage(content=final_response, role=MessageRole.ASSISTANT, session_id=session_id)
        self.chat_session_repo.add_message_to_session(session_id=session_id, message=ai_msg)
        
        # Step 6: Return structured response
        return ChatMessage(
                content=final_response,
                role=MessageRole.ASSISTANT,
                session_id=session_id
            )
    
    def _get_or_create_session(self, user_id: int, session_id: str) -> ChatSession:
        """Get an existing session or create a new one if it doesn't exist."""
        try:
            # Try to get the session
            session = self.chat_session_repo.get_session_by_id(session_id)
            if session:
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
        
        return self.chat_session_repo.create_session(new_session)