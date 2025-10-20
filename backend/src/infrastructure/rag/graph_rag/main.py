from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# --- Import your modular components ---
from backend.src.infrastructure.rag.graph_rag.embedder.google_emb import \
    get_retriever_tool
from backend.src.infrastructure.rag.graph_rag.llm.llm import get_llm
from backend.src.infrastructure.rag.graph_rag.prompts import SYSTEM_PROMPT
from backend.src.infrastructure.rag.graph_rag.tools.tavily_search import \
    search_tool


# --- 1. Define the State ---
class State(TypedDict):
    messages: Annotated[list, add_messages]

# --- 2. Initialize your Tools and LLM ---
retriever_tool = get_retriever_tool()
llm = get_llm()

# Create a list of all tools the LLM can use
all_tools = [retriever_tool, search_tool]

# Bind the tools to the LLM
llm_with_tools = llm.bind_tools(all_tools)


# --- 3. Define the Graph Nodes ---
def call_model(state: State):
    """The primary node that calls the LLM. It can decide to respond or call a tool."""
    print("---NODE: Calling Model---")
     
    messages = state["messages"]
    if not messages or messages[0].type != "system":
        messages = [("system", SYSTEM_PROMPT)] + messages
        
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# The ToolNode now knows about both the search tool and the retriever tool
tool_node = ToolNode(all_tools)


# --- 4. Define the Router Logic ---
def should_call_tools(state: State):
    """Checks the last message for to determine whether to call a tool or end the graph."""
    print("---EDGE: Checking for Tool Calls---")
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        print("Decision: Call tool(s)")
        return "call_tool"
    print("Decision: End graph")
    return "__end__"


# --- 5. Build the Graph ---
graph_builder = StateGraph(State)

graph_builder.add_node("llm", call_model)
graph_builder.add_node("call_tool", tool_node)

graph_builder.set_entry_point("llm")
graph_builder.add_conditional_edges(
    "llm",
    should_call_tools
)
graph_builder.add_edge("call_tool", "llm")


memory = MemorySaver()

app = graph_builder.compile(checkpointer=memory)

def main():
    print("Graph compiled. You can now chat with the multi-tool agent.")
    thread_id = "thread_1"
    config = {"configurable": {"thread_id": thread_id}}
    while True:
        
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            break

        events = app.stream(
            {"messages": [("user", user_input)]},
            config=config, #type: ignore
            stream_mode="values",
        )
        for event in events:
            event["messages"][-1].pretty_print()

if __name__ == "__main__":
    main()