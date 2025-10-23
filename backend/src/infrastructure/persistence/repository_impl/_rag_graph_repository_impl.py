from typing import Any, Dict, List
from backend.src.application.interfaces._rag_repository import IRAGRepository
from backend.src.infrastructure.rag.graph_builder import build_langgraph_rag_graph


class LangGraphRAGRepository(IRAGRepository):
    def __init__(self, vector_repo, embedding_repo, chat_repo):
        self.vector_repo = vector_repo
        self.embedding_repo = embedding_repo
        self.chat_repo = chat_repo
        self.graph = build_langgraph_rag_graph()
    
    def initialize_graph(self) -> Any:
        """Initialize and return the RAG graph."""
        return self.graph
    
    def run_rag_pipeline(self, session_id: str, user_query: str) -> str:
        state = {"session_id": session_id, "query": user_query}
        result = self.graph.invoke(state) #type: ignore
        return result["answer"]
        
    def summarize_history(self, history: List[Dict[str, Any]]) -> str:
        """
        Summarize chat history for context.
        
        Args:
            history: A list of message dictionaries with 'role' and 'content' keys
            
        Returns:
            A concise summary of the conversation
        """
        if not history:
            return ""
        
        # Convert history to a format suitable for the prompt
        formatted_history = ""
        for msg in history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            formatted_history += f"{role.capitalize()}: {content}\n"
        
        # Create a state with a summarization request
        summary_state = {
            "session_id": "summarization",
            "query": f"""Please summarize the following conversation history concisely:
            
            {formatted_history}
            
            Focus on capturing key topics, questions, and information that would be helpful for continuing the conversation.
            """
        }
        
        # Use the RAG pipeline to generate a summary
        try:
            result = self.graph.invoke(summary_state) #type: ignore
            return result.get("answer", "Previous conversation about various topics.")
        except Exception as e:
            # Fallback to a basic summary if the LLM call fails
            return f"Past conversation with {len(history)} messages about various topics."
