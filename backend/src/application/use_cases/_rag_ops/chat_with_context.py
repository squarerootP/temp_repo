from typing import Optional

from backend.src.application.interfaces.rag_interfaces.chat_session_repository import \
    IChatSessionRepository
from backend.src.application.interfaces.rag_interfaces.rag_repository import \
    IRAGRepository
from backend.src.domain.entities.rag_entities.chat_history import (ChatMessage,
                                                                   ChatSession,
                                                                   MessageRole)
from backend.src.domain.exceptions.chat_exceptions import (
    MessageGenerationNotFound)
from backend.src.infrastructure.config.settings import settings

MAX_HISTORY_MSG_LEN_TO_RETRIEVE = settings.MAX_HISTORY_MSG_LEN_TO_RETRIEVE

class ChatWithContext:
    """
    Use case: Use the document hash to find the document that the user wants to chat about.
    """

    def __init__(
        self,
        rag_repo: IRAGRepository,
        chat_session_repo: IChatSessionRepository,
        hash: str,
    ):
        self.rag_repo = rag_repo
        self.chat_session_repo = chat_session_repo
        self.hash = hash

    def generate_response(
        self, current_user, session_id: str, query: str, hash: str
    ) -> ChatMessage:
        
        # Get or create session
        db_chat_session = self._get_or_create_session(session_id, current_user.user_id)

        if not db_chat_session.messages:
            revised_query = query
        else:
            history_msg = db_chat_session.messages[-MAX_HISTORY_MSG_LEN_TO_RETRIEVE:]
            formatted_history = [
                {"role": msg.role.value, "content": msg.content} for msg in history_msg
            ]
            print(
                "=======Here are the last 4 of the formatted history (for short): ",
                formatted_history[-4:],
            )
            summarized_history = self.rag_repo.summarize_history(formatted_history)
            print("=======Here is summarized history:", summarized_history)
            revised_query = self.rag_repo.revise_query_with_context(
                query, summarized_history
            )
            print("=======Here is revised query:", revised_query)
        
        # PERSIST USER MESSAGE
        user_msg = ChatMessage(
            content=query, role=MessageRole.USER, session_id=session_id
            )
        self.chat_session_repo.add_message_to_session(session_id, user_msg)

        response = self.rag_repo.answer_query_with_specific_document(
            user_query=revised_query, document_hash=hash
            )
        if not response:
            raise MessageGenerationNotFound("No response generated for the query.")
        
        # PERSIST AI MESSAGE
        ai_msg = ChatMessage(
            content=response, role=MessageRole.ASSISTANT, session_id=session_id
            )
        self.chat_session_repo.add_message_to_session(
            session_id=session_id, message=ai_msg
            )
        
        return ChatMessage(
            content=response, role=MessageRole.ASSISTANT, session_id=session_id
        )

    def _get_or_create_session(self, session_id: str, user_id: int) -> ChatSession:
        db_chat_session = self.chat_session_repo.get_session_by_id(session_id)
        if not db_chat_session:
            chat_session = self.chat_session_repo.create_session(
                ChatSession(session_id=session_id, messages=[], user_id=user_id)
            )
            return chat_session
        return db_chat_session