import json
import re
from typing import Annotated, Any, List, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from backend.src.infrastructure.rag.graph_rag.prompts import SYSTEM_PROMPT
from backend.src.infrastructure.rag.tools.llm_tool import get_llm
from backend.src.infrastructure.rag.tools.retriever_tool import \
    get_retriever_tool
from backend.src.infrastructure.rag.tools.search_tool import search_tool


# --- Utility ---
def to_messages(msgs):
    formatted = []
    for m in msgs:
        if isinstance(m, tuple):
            role, content = m
            if role == "user":
                formatted.append(HumanMessage(content=content))
            elif role == "system":
                formatted.append(SystemMessage(content=content))
        else:
            formatted.append(m)
    return formatted


# --- State ---
class State(TypedDict):
    messages: Annotated[List[Any], add_messages]


# --- Search Node ---
class EnhancedSearchNode:
    def __init__(self, search_tool):
        self.search_tool = search_tool

    def __call__(self, state: State):
        last_message = state["messages"][-1]
        query = None

        # Try to extract structured query
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            for tc in last_message.tool_calls:
                if tc["name"] == "tavily_search":
                    query = tc["args"].get("query")
                    break

        if not query:
            match = re.search(r'"query"\s*:\s*"([^"]+)"', getattr(last_message, "content", ""))
            query = match.group(1) if match else "latest information"

        print(f"Searching for: {query}")
        result = self.search_tool.invoke({"query": query})
        return {"messages": [ToolMessage(content=result, tool_call_id="tavily_search", name="tavily_search")]}


# --- Main graph builder ---
def build_langgraph_rag_graph():
    retriever_tool = get_retriever_tool()
    llm = get_llm()
    tools = [retriever_tool, search_tool]
    llm_with_tools = llm.bind_tools(tools, strict=False)

    def call_model(state: State):
        messages = to_messages(state["messages"])
        if not any(m.type == "system" for m in messages):
            messages.insert(0, SystemMessage(content=SYSTEM_PROMPT))
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    retriever_node = ToolNode([retriever_tool])
    search_node = EnhancedSearchNode(search_tool)

    def route_after_llm(state: State):
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            tool_names = [tc["name"] for tc in last_message.tool_calls]
            if "Document_Retriever" in tool_names:
                return "call_retriever"
            if "tavily_search" in tool_names:
                return "call_search"
        return END

    # --- Build Graph ---
    graph = StateGraph(State)
    graph.add_node("reasoning", call_model)
    graph.add_node("call_retriever", retriever_node)
    graph.add_node("call_search", search_node)
    graph.add_edge(START, "reasoning")

    graph.add_conditional_edges("reasoning", route_after_llm, {
        "call_retriever": "call_retriever",
        "call_search": "call_search",
        END: END,
    })

    graph.add_edge("call_retriever", "reasoning")
    graph.add_edge("call_search", "reasoning")

    return graph.compile()
