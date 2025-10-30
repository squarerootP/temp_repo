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
from backend.src.application.interfaces.rag_interfaces.document_repository import \
    IDocumentRepository
from backend.src.application.interfaces.rag_interfaces.rag_repository import \
    IRAGRepository
from backend.src.application.interfaces.rag_interfaces.vectorstore_repo import \
    IVectorStoreRepository
from backend.src.domain.entities.rag_entities.chat_history import (ChatMessage,
                                                                   MessageRole)
from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.graph_builder import \
    build_graph
from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.llm.llm import (
    get_big_llm, get_decent_llm, get_small_llm)

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
        self.graph = build_graph()
        self.decent_llm = get_decent_llm()
        self.big_llm = get_big_llm()    

    def initialize_graph(self) -> Any:
        """Return the compiled graph-like object (framework-agnostic)."""
        return self.graph

    # ---------- Helpers ----------
    def _run_graph_and_get_last_content(self, messages_payload: List[tuple], query: str, document_hash: Optional[str] = None) -> str:
        """
        Run the compiled graph with given messages payload and return the final message.content.
        """
        try:
            events = self.graph.stream(
                {
                    "query": query,
                    "messages": messages_payload,  # list of ("user", text)
                    "documents": [],
                    "search_results": [],
                    "web_search": "yes",
                    "document_hash": document_hash,
                },
                stream_mode="values",
            )

            last_content: Optional[str] = None
            for event in events:
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
    def answer_query(self, user_query: str) -> str:
        """
        Run the full RAG pipeline for a query and persist conversation messages.

        Workflow:
        - Persist the user message to chat repo
        - Run graph (LLM + tools) and obtain assistant answer
        - Persist assistant message
        - Return assistant text
        """
        try:
            messages_payload = [("user", user_query)]
            assistant_text = self._run_graph_and_get_last_content(messages_payload, query=user_query)

            if not assistant_text:
                assistant_text = "I'm sorry — I couldn't generate an answer at the moment."

            return assistant_text

        except Exception as e:
            logger.exception("answer_query failed: %s", e)
            return "I'm sorry, something went wrong while processing your request."

    def summarize_history(self, formatted_history: List[Dict[str, Any]]) -> str:
        """
        Summarize chat history for context.

        Default: create a simple summarization prompt and run the graph to produce a summary.
        If the graph fails, fallback to a short heuristic summary.
        """
        if not formatted_history:
            return ""

        summarization_prompt = (
            "Please provide a short concise summary of the conversation below. "
            "Focus on key topics, questions, and any details which would help continue the conversation.\n\n"
            f"{formatted_history}\n\nSummary:"
        )

        # Run the graph with a system/system-like prompt then a user summarization request
        try:
            result = self.decent_llm.invoke(summarization_prompt).content
            return result or f"Conversation of {len(history)} messages about various topics." #type: ignore
        except Exception as e:
            logger.exception("summarize_history fallback: %s", e)
            return f"Conversation of {len(formatted_history)} messages about various topics."

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
        You are a precise text rewriting engine. 
        Your goal is to rewrite the user's question so that it naturally and concisely includes any useful information from the given context.

        Rules:
        - Output ONLY the rewritten question. Do NOT include any explanations, labels, or formatting.
        - The rewritten question must sound natural and human-like.
        - If the user’s question already makes sense without the context, keep it mostly the same.
        - If the context provides missing details or references that clarify the query, integrate them smoothly.
        - If the user’s query is vague, incomplete, or ambiguous, rewrite it into a clearer, more general question.
        - If the query is completely unrelated to the context, ignore the context and output a neutral, general rewrite.
        - If you don’t have enough information to confidently rewrite, just return the original text unchanged.
        - If the user greets or says thanks, keep it as is.

        Context:
        {context}

        User’s original question:
        {query}

        Rewritten question:
        """
        
        # Use the graph to produce a refined query
        refined = self.big_llm.invoke(prompt).content
        return refined or f"{query} {context}" # type: ignore

    def answer_query_with_specific_document(self, session_id: str, user_query: str, document_hash: Optional[str]) -> str:
        """
        Answer a query but instruct the retrieval component to focus on a specific document.

        Heuristic used:
        - Inject a system message that instructs retriever/tools/LLM to prioritize the document with given hash.
        - Then run the usual graph pipeline.
        - Persist messages to chat session.
        """
        
        try:
        
            messages_payload = [
                ("user", user_query),
            ]

            assistant_text = self._run_graph_and_get_last_content(messages_payload, user_query, document_hash=document_hash)

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
