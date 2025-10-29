from backend.src.application.interfaces.rag_interfaces.chat_session_repository import \
    IChatSessionRepository
from backend.src.application.interfaces.rag_interfaces.rag_repository import \
    IRAGRepository
from backend.src.domain.entities.rag_entities.chat_history import (ChatMessage,
                                                                   ChatSession,
                                                                   MessageRole)
from backend.src.domain.exceptions.chat_exceptions import ChatHistoryNotFound
from typing import Optional

class ChatWithContext:
    """
    Use case: Use the document hash to find the document that the user wants to chat about.
    """
    
    def __init__(
        self, 
        rag_repo: IRAGRepository,
        chat_session_repo: IChatSessionRepository,
        hash: Optional[str] = None 
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

        # Get or create session
        db_chat_session = self.chat_session_repo.get_session_by_id(session_id)
        if not db_chat_session:
            chat_session = self.chat_session_repo.create_session(
                ChatSession(
                    session_id=session_id,
                    messages=[],
                    user_id=user_id
                ))
            revised_query = query
        else:
            chat_session = db_chat_session
            history_msg = chat_session.messages[-10:]
            formatted_history = [{"role": msg.role.value, "content": msg.content} 
                                for msg in history_msg]
            summarized_history = self.rag_repo.summarize_history(formatted_history)
    
            revised_query = self.rag_repo.revise_query_with_context(query, summarized_history)
            
        # Add user message to session
        user_msg = ChatMessage(content=query, role=MessageRole.USER, session_id=session_id)
        self.chat_session_repo.add_message_to_session(session_id, user_msg)
        
        # Get response from RAG system
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
    