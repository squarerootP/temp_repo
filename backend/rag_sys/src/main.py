import traceback
from typing import Annotated, List, cast

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.runnables.config import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command
from typing_extensions import TypedDict

from backend.rag_sys.src.adapter.llms.cerebras import llm
from backend.rag_sys.src.adapter.persistence.logger import _log
from backend.rag_sys.src.adapter.tools.human_assistance import human_assistance
from backend.rag_sys.src.adapter.tools.tavily_search import search_tool
from backend.rag_sys.src.infrastructure.settings import env_settings


# State:
class State(TypedDict):
    messages : Annotated[List[BaseMessage], add_messages]
    name: str
    birthday: str

# Define the tools set
tools = [search_tool, human_assistance]

# Binding the llm with the tools:
llm_with_tools = llm.bind_tools(tools=tools)

# Chatbot
def chatbot(state: State):
    try:
        result = llm_with_tools.invoke(state["messages"], timeout=60)
        _log(f"Chatbot result: {result}")
        return {"messages": [result]}
    except Exception as e:
        err_msg = f"Error in chatbot: {e}"
        _log(err_msg)
        _log(traceback.format_exc())
        return {"messages": [HumanMessage(content=err_msg)]}

# Resume after the interrupt:
def finalize(state: State):
    return {"messages": f"Finalized: {state['messages']}"}

# Graph config:
tool_node = ToolNode(tools=tools)
memory = InMemorySaver()
config = cast(RunnableConfig, {"configurable": {"thread_id": "1"}})

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)
# graph_builder.add_node("human_assistance", human_assistance)
# graph_builder.add_edge("tools", "human_assistance")
# graph_builder.add_node("finalize", finalize)
# graph_builder.add_edge("human_assistance", "finalize")

graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

graph = graph_builder.compile(checkpointer=memory)

# Stream:
def stream_graph_updates(user_input: str):
    _log("\nUser input: " + user_input)
    try:
        human_msg = HumanMessage(content=user_input)
        event_count = 0
        for event in graph.stream(
            {"messages": [human_msg]},
            config=config,
            stream_mode="values"
        ):
            event_count +=1
            _log(f"Event {event_count}: {event}")
            
            if "messages" in event:
                messages = event["messages"]
                last_msg = messages[-1]

                if hasattr(last_msg, "content") and getattr(last_msg, "type", "") == "ai" and last_msg.content:
                    print(f"Assistant: {last_msg.content}")
        _log(f"Stream completed with {event_count} events")

    except Exception as e:
        err_msg = f"Error during stream: {e}"
        _log(err_msg)
        _log(traceback.format_exc()) 

def test():
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ['exit', 'q', 'quit'] :
                print("Goodbye!")
                break
            print("Processing your request...")
            stream_graph_updates(user_input)
        except Exception as e:
            _log(f"Main loop error: {e}")
            _log(traceback.format_exc())
            print(f"Error: {e}")
def main():
    config = {"configurable": {"thread_id": "1"}}
    events = graph.stream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "I'm learning LangGraph. "
                        "Could you do some research on it for me?"
                    ),
                },
            ],
        },
        config,
        stream_mode="values",
    )
    for event in events:
        if "messages" in event:
            event["messages"][-1].pretty_print()
if __name__ == "__main__":
    # main()
    test()