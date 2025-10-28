import json
import re
from typing import Annotated, Any, List, Literal, TypedDict

from langchain_core.messages import (AIMessage, HumanMessage, SystemMessage,
                                     ToolMessage)
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from backend.src.infrastructure.rag.graph_rag.prompts import SYSTEM_PROMPT
from backend.src.infrastructure.rag.tools.llm_tool import get_llm
from backend.src.infrastructure.rag.tools.retriever_tool import \
    get_retriever_tool
from backend.src.infrastructure.rag.tools.search_tool import search_tool


# --- State ---
class State(TypedDict):
    messages: Annotated[List[Any], add_messages]

# --- Main graph builder ---
def build_langgraph_rag_graph():
    retriever_tool = get_retriever_tool()
    llm = get_llm()
    llm_with_tools = llm.bind_tools([retriever_tool])

    def call_llm(state: State):
        print("---NODE: Calling Model---")
        
        
        messages = state["messages"]
        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

        response = llm_with_tools.invoke(messages)
        
        return {"messages": [response]}
    
    retriever_node = ToolNode([retriever_tool], name = "retriever_node")
    
    def router(state: State) -> Literal["retriever_node", "__end__"]:
        print("---NODE: Router---")
        last_message = state["messages"][-1]
        
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            print("---Router: Rerouting to tools---")
            return "retriever_node"
        
        print("---Router: Routing to end---")
        return "__end__"

    # --- Build Graph ---
    graph = StateGraph(State)
    
    graph.add_node("llm_node", call_llm)
    graph.add_node("retriever_node", retriever_node)

    graph.set_entry_point("llm_node")
    graph.add_conditional_edges(
        "llm_node",
        router,           
        {
            "retriever_node": "retriever_node",
            "__end__": END          
        }
    )
    graph.add_edge("retriever_node", "llm_node") 

    return graph.compile()

