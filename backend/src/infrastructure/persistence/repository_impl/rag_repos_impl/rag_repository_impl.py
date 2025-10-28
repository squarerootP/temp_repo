import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

"""Single authoritative RAG repository implementation.

This file provides the concrete RAG implementation used across the app.
There used to be a duplicate graph-only implementation in
`_rag_graph_repository_impl.py` which has been removed. Keep this class
as the canonical provider of the IRAGRepository contract.
"""

from backend.src.application.interfaces.rag_interfaces.chat_session_repository import \
    IChatSessionRepository
from backend.src.application.interfaces.rag_interfaces.document_repository import (
    IDocumentRepository, IVectorStoreRepository)
from backend.src.application.interfaces.rag_interfaces.rag_repository import \
    IRAGRepository
from backend.src.domain.entities.rag_entities.chat_history import (ChatMessage,
                                                                   MessageRole)
from backend.src.infrastructure.rag.graph_builder import \
    build_langgraph_rag_graph
from backend.src.infrastructure.rag.tools.llm_tool import get_llm

logger = logging.getLogger(__name__)


class LangGraphRAGRepositoryImpl(IRAGRepository):
    """LangGraph-based RAG repository implementing IRAGRepository.

    Constructor accepts the repositories it may orchestrate. Only the
    chat repository and the compiled graph are required for answering
    queries, but vector/embedding repositories can be provided for
    extended functionality or future hooks.
    """

    def __init__(
        self,
        vector_repo: Optional[IVectorStoreRepository] = None,
        chat_repo: Optional[IChatSessionRepository] = None,
    ):
        self.vector_repo = vector_repo
        self.chat_repo = chat_repo
        self.graph = build_langgraph_rag_graph()
        self.simple_llm = get_llm()

    def initialize_graph(self) -> Any:
        """Return the compiled graph-like object (framework-agnostic)."""
        return self.graph

    # ---------- Helpers ----------
    def _run_graph_and_get_last_content(self, messages_payload: List[tuple]) -> str:
        """
        Run the compiled graph with given messages payload and return the final message.content.

        messages_payload: list of tuples like ("user", "text") or ("system", "text")
        """
        try:
            # stream returns an iterator of events; we collect and return the last message content
            events = self.graph.stream(
                {"messages": messages_payload},
                stream_mode="values",
            )

            last_content: Optional[str] = None
            for event in events:
                # safety checks - event["messages"] is expected
                if event and "messages" in event and event["messages"]:
                    last_msg = event["messages"][-1]
                    content = getattr(last_msg, "content", None)
                    if content:
                        last_content = content

            return last_content or ""
        except Exception as e:
            logger.exception("Error while running graph: %s", e)
            return ""

    # ---------- IRAG methods ----------
    def answer_query(self, session_id: str, user_query: str) -> str:
        """
        Run the full RAG pipeline for a query and persist conversation messages.

        Workflow:
        - Persist the user message to chat repo
        - Run graph (LLM + tools) and obtain assistant answer
        - Persist assistant message
        - Return assistant text
        """
        try:
            # persist user message
            user_msg = ChatMessage(content=user_query, role=MessageRole.USER, session_id=session_id)

            # Run graph with simple payload
            messages_payload = [("user", user_query)]
            assistant_text = self._run_graph_and_get_last_content(messages_payload)

            if not assistant_text:
                assistant_text = "I'm sorry — I couldn't generate an answer at the moment."

            return assistant_text

        except Exception as e:
            logger.exception("answer_query failed: %s", e)
            return "I'm sorry, something went wrong while processing your request."

    def summarize_history(self, history: List[Dict[str, Any]]) -> str:
        """
        Summarize chat history for context.

        Default: create a simple summarization prompt and run the graph to produce a summary.
        If the graph fails, fallback to a short heuristic summary.
        """
        if not history:
            return ""
        
        formatted_history = history

        summarization_prompt = (
            "Please provide a short concise summary of the conversation below. "
            "Focus on key topics, questions, and any details which would help continue the conversation.\n\n"
            f"{formatted_history}\n\nSummary:"
        )

        # Run the graph with a system/system-like prompt then a user summarization request
        try:
            result = self.simple_llm.invoke(summarization_prompt).content
            return result or f"Conversation of {len(history)} messages about various topics." #type: ignore
        except Exception as e:
            logger.exception("summarize_history fallback: %s", e)
            return f"Conversation of {len(history)} messages about various topics."

    def revise_query_with_context(self, query: str, context: str) -> str:
        """
        Revise user query by inserting the summarized context to give the RAG pipeline
        a more context-rich question. This implementation uses a simple deterministic
        rewrite but can be replaced by an LLM call for richer rewrites.
        """
        if not context:
            return query

        # Small, explicit instruction to the LLM to prefer context while keeping original intent
        prompt = f"""
        You are a text rewriting engine. 
        You will ONLY output a single rewritten user question, nothing else.

        Rewrite the following question so that it includes the relevant context.
        Keep it concise and natural.
        If you think you don't have enough information to rewrite the user message, just return the original text.

        Context:
        {context}

        Original question:
        {query}

        Rewritten question:
        """

        # Use the graph to produce a refined query
        refined = self.simple_llm.invoke(prompt).content
        return refined or f"{query} {context}" # type: ignore

    def answer_query_with_specific_document(self, session_id: str, user_query: str, doc_hash: str) -> str:
        """
        Answer a query but instruct the retrieval component to focus on a specific document.

        Heuristic used:
        - Inject a system message that instructs retriever/tools/LLM to prioritize the document with given hash.
        - Then run the usual graph pipeline.
        - Persist messages to chat session.

        NOTE: For stronger enforcement, implement a retriever method that accepts doc_hash
        and use it inside your retriever tool (recommended).
        """
        
        try:
            # Persist user message
            user_msg = ChatMessage(content=user_query, role=MessageRole.USER, session_id=session_id)
            
            # Create a system instruction asking tools to focus on the given doc_hash
            system_instruction = (
                f"ONLY use the document identified by hash '{doc_hash}' for retrieval. "
                "If the document does not contain an answer, say you cannot find the requested information."
            )

            messages_payload = [
                ("system", system_instruction),
                ("user", user_query),
            ]

            assistant_text = self._run_graph_and_get_last_content(messages_payload)

            if not assistant_text:
                assistant_text = "I'm sorry — I couldn't find an answer in the specified document."

            # Persist assistant message
            ai_msg = ChatMessage(content=assistant_text, role=MessageRole.ASSISTANT, session_id=session_id)
            try:
                if self.chat_repo:
                    self.chat_repo.add_message_to_session(session_id=session_id, message=ai_msg)
            except Exception:
                logger.exception("Failed to persist assistant message (specific doc) for session %s", session_id)

            return assistant_text

        except Exception as e:
            logger.exception("answer_query_with_specific_document failed: %s", e)
            return "I'm sorry, something went wrong while processing your request."
