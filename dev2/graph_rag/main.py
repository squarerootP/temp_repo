# backend/src/infrastructure/rag/graph_rag/main.py

# json and re are no longer needed
from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# --- Import your modular components ---
from backend.src.infrastructure.rag.graph_rag.embedder.google_emb import \
    get_retriever_tool
from backend.src.infrastructure.rag.graph_rag.llm.llm import get_llm
from backend.src.infrastructure.rag.graph_rag.prompts import SYSTEM_PROMPT
from backend.src.infrastructure.rag.graph_rag.tools.tavily_search import \
    search_tool
import logging

logging.getLogger("langchain").setLevel(logging.ERROR)

# --- Helper Functions ---

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


# --- 1. Define the State ---
class State(TypedDict):
    messages: Annotated[list, add_messages]


# --- 2. Initialize your Tools and LLM ---
retriever_tool = get_retriever_tool()
llm = get_llm()
tools = [retriever_tool, search_tool]
# We no longer use llm.bind_tools()


# --- 3. Define Graph Nodes ---
def call_model(state: State):
    print("---NODE: Calling Model---")

    messages = to_messages(state["messages"])

    if not any(m.type == "system" for m in messages):
        messages.insert(0, SystemMessage(content=SYSTEM_PROMPT))

    # Pass the tools list directly to the invoke method
    response = llm.invoke(messages, tools=tools)

    return {"messages": [response]}


# --- Enhanced Search Node is REMOVED ---


# Tool nodes (Now standard for both)
retriever_node = ToolNode([retriever_tool])
search_node = ToolNode([search_tool])


# --- 4. Define Router Logic (Simplified) ---
def route_after_llm(state: State):
    """
    After LLM call, route based on tool calls:
    - If retriever_tool -> call retriever
    - If search_tool -> call search
    - No tool calls -> END
    """
    print("---EDGE: Routing after LLM Call---")
    last_message = state["messages"][-1]

    # Check for standard tool_calls format
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        print("Decision: No tool calls, ending.")
        return END
        
    tool_names = [tc["name"] for tc in last_message.tool_calls]
    print(f"Tool names in message: {tool_names}")
    
    # Your prompt forces this order, and this logic enforces it.
    if "Document_Retriever" in tool_names:
        # Keep only the Document_Retriever tool call
        last_message.tool_calls = [tc for tc in last_message.tool_calls if tc["name"] == "Document_Retriever"]
        print("Decision: Call Retriever")
        return "call_retriever"
    
    elif "tavily_search" in tool_names:
        # Keep only the tavily_search tool call
        last_message.tool_calls = [tc for tc in last_message.tool_calls if tc["name"] == "tavily_search"]
        print("Decision: Call Web Search")
        return "call_search"
    
    print("Decision: No routable tool calls found, ending.")
    return END

# --- 5. Build the Graph ---
graph_builder = StateGraph(State)

# Nodes
graph_builder.add_node("reasoning", call_model)
graph_builder.add_node("call_retriever", retriever_node)
graph_builder.add_node("call_search", search_node) # Uses the standard ToolNode

# Entry → always go to reasoning first
graph_builder.add_edge(START, "reasoning")

# Conditional edges after reasoning
graph_builder.add_conditional_edges(
    "reasoning", 
    route_after_llm,
    {
        "call_retriever": "call_retriever",
        "call_search": "call_search",
        END: END
    }
)

# After tool usage, go back to reasoning to incorporate new information
graph_builder.add_edge("call_retriever", "reasoning")
graph_builder.add_edge("call_search", "reasoning")

# Memory (Enabled)
memory = MemorySaver()
app = graph_builder.compile(checkpointer=memory)
# app = graph_builder.compile() # Old version


# --- 6. Chat Interface ---
def main():
    print("Graph compiled. Multi-tool RAG agent ready.")
    # Use a unique thread_id for each conversation if you want separate memories
    thread_id = "thread_1" 
    config = {"configurable": {"thread_id": thread_id}}

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            break

        events = app.stream(
            {"messages": [("user", user_input)]},
            config=config,  # type: ignore
            stream_mode="values",
        )
        for event in events:
            event["messages"][-1].pretty_print()


if __name__ == "__main__":
    main()