import json
import re
from typing import Annotated, TypedDict, Dict, Any, List

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# --- Import your modular components ---
from backend.src.infrastructure.rag.graph_rag.embedder.google_emb import get_retriever_tool
from backend.src.infrastructure.rag.graph_rag.llm.llm import get_llm
from backend.src.infrastructure.rag.graph_rag.prompts import SYSTEM_PROMPT
from backend.src.infrastructure.rag.graph_rag.tools.tavily_search import search_tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

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
# Bind both tools
llm_with_tools = llm.bind_tools(tools, strict=False) 


# --- 3. Define Graph Nodes ---
def call_model(state: State):
    print("---NODE: Calling Model---")

    messages = to_messages(state["messages"])

    if not any(m.type == "system" for m in messages):
        messages.insert(0, SystemMessage(content=SYSTEM_PROMPT))

    # use the bound llm
    response = llm_with_tools.invoke(messages)

    return {"messages": [response]}


# --- Enhanced Search Node ---
class EnhancedSearchNode:
    def __init__(self, search_tool):
        self.search_tool = search_tool
        
    def __call__(self, state: State):
        last_message = state["messages"][-1]
        query = None
        
        # Extract query from tool_calls if available
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            for tool_call in last_message.tool_calls:
                if tool_call["name"] == "tavily_search":
                    query = tool_call["args"].get("query")
                    break
        
        # Fallback: try to parse from content
        if not query and hasattr(last_message, "content") and last_message.content:
            try:
                # Look for JSON pattern
                json_match = re.search(r'(\{.*"type"\s*:\s*"function".*\})', last_message.content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    tool_call = json.loads(json_str)
                    
                    if tool_call.get("name") == "tavily_search":
                        query = tool_call.get("parameters", {}).get("query", "")
                else:
                    # Simple regex fallback
                    match = re.search(r'"query"\s*:\s*"([^"]+)"', last_message.content)
                    if match:
                        query = match.group(1)
            except Exception as e:
                print(f"Error parsing search query: {e}")
        
        # Default query if all else fails
        if not query:
            # Try to extract a query from previous human message
            for msg in reversed(state["messages"]):
                if isinstance(msg, HumanMessage):
                    query = msg.content
                    break
            if not query:
                query = "latest information"
            
        print(f"Searching for: {query}")
        result = self.search_tool.invoke({"query": query})
        
        return {"messages": [ToolMessage(content=result, tool_call_id="tavily_search", name="tavily_search")]}


# Tool nodes
retriever_node = ToolNode([retriever_tool])
search_node = EnhancedSearchNode(search_tool)


# --- 4. Define Router Logic ---
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
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_names = [tc["name"] for tc in last_message.tool_calls]
        print(f"Tool names in message: {tool_names}")
        
        # Filter tool calls to include only the one we're routing to
        if "Document_Retriever" in tool_names:
            # Keep only the Document_Retriever tool call
            filtered_calls = [tc for tc in last_message.tool_calls if tc["name"] == "Document_Retriever"]
            last_message.tool_calls = filtered_calls
            print("Decision: Call Retriever (filtered other tool calls)")
            return "call_retriever"
        elif "tavily_search" in tool_names:
            # Keep only the tavily_search tool call
            filtered_calls = [tc for tc in last_message.tool_calls if tc["name"] == "tavily_search"]
            last_message.tool_calls = filtered_calls
            print("Decision: Call Web Search (filtered other tool calls)")
            return "call_search"
    
    # Extract JSON-formatted tool calls from the content
    if hasattr(last_message, "content") and last_message.content:
        content = last_message.content
        
        # Try to find and parse JSON in the content
        try:
            # Look for JSON pattern
            json_match = re.search(r'(\{.*"type"\s*:\s*"function".*\})', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                tool_call = json.loads(json_str)
                
                if tool_call.get("name") == "tavily_search":
                    print("Decision: Found JSON tavily_search tool call")
                    return "call_search"
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Error parsing JSON tool call: {e}")
        
        # Fallback for simpler detection
        if "tavily_search" in content and "function" in content.lower():
            print("Decision: Detected tavily_search in content text")
            return "call_search"
    
    print("Decision: No tool calls, ending.")
    return END


# --- 5. Build the Graph ---
graph_builder = StateGraph(State)

# Nodes
graph_builder.add_node("reasoning", call_model)
graph_builder.add_node("call_retriever", retriever_node)
graph_builder.add_node("call_search", search_node)

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

# Memory
# memory = MemorySaver()
# app = graph_builder.compile(checkpointer=memory)
app = graph_builder.compile()

# --- 6. Chat Interface ---
def main():
    print("Graph compiled. Multi-tool RAG agent ready.")
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