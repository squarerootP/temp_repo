import traceback
from typing import AsyncIterator, cast

from langchain_core.messages import HumanMessage
from langchain_core.runnables.config import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from backend.src.domain.entities.rag_state import ChatState
from backend.src.application.interfaces.chat_interface import RAGServiceInterface
from backend.src.infrastructure.rag.experimental.adapters.llms.cerebras import llm
from backend.src.infrastructure.rag.experimental.adapters.tools.tavily_search import (
    search_tool,
)
from backend.src.infrastructure.rag.experimental.adapters.tools.human_assistance import (
    human_assistance,
)
from backend.src.infrastructure.rag.experimental.adapters.persistence.logger import _log


class LangGraphRAGService(RAGServiceInterface):
    """
    Dev-only RAG service. Uses experimental adapters copied from rag_sys.
    Not intended for production.
    """

    def __init__(self):
        self.tools = [search_tool, human_assistance]
        self.llm_with_tools = llm.bind_tools(tools=self.tools)
        self.memory = InMemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self):
        tool_node = ToolNode(tools=self.tools)
        graph_builder = StateGraph(ChatState)
        graph_builder.add_node("chatbot", self._chatbot_node)
        graph_builder.add_node("tools", tool_node)
        graph_builder.add_conditional_edges("chatbot", tools_condition)
        graph_builder.add_edge("tools", "chatbot")
        graph_builder.add_edge(START, "chatbot")
        return graph_builder.compile(checkpointer=self.memory)

    def _chatbot_node(self, state: ChatState):
        try:
            result = self.llm_with_tools.invoke(state["messages"], timeout=60)
            _log(f"Chatbot result: {result}")
            return {"messages": [result]}
        except Exception as e:
            err_msg = f"Error in chatbot: {e}"
            _log(err_msg)
            _log(traceback.format_exc())
            return {"messages": [HumanMessage(content=err_msg)]}

    async def stream_chat(self, user_input: str, thread_id: str) -> AsyncIterator[dict]:
        _log(f"\nUser input: {user_input}")
        config = cast(RunnableConfig, {"configurable": {"thread_id": thread_id}})

        try:
            human_msg = HumanMessage(content=user_input)
            event_count = 0

            for event in self.graph.stream(
                {"messages": [human_msg]}, config=config, stream_mode="values"
            ):
                event_count += 1
                _log(f"Event {event_count}: {event}")
                yield event

            _log(f"Stream completed with {event_count} events")
        except Exception as e:
            err_msg = f"Error during stream: {e}"
            _log(err_msg)
            _log(traceback.format_exc())
            raise

    async def process_message(self, user_input: str, thread_id: str) -> str:
        response = ""
        async for event in self.stream_chat(user_input, thread_id):
            if "messages" in event:
                last_msg = event["messages"][-1]
                if hasattr(last_msg, "content") and getattr(last_msg, "type", "") == "ai":
                    response = last_msg.content
        return response
