from langchain.schema.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated, Literal

from dev.graph_rag.embedder.google_emb import get_retriever_tool
from dev.graph_rag.llm.llm import get_llm
from dev.graph_rag.prompts import SYSTEM_PROMPT


class State(TypedDict):
    messages: Annotated[list, add_messages]


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

retriever_node = ToolNode([retriever_tool], name="retriever_node")

def router(state: State) -> Literal["retriever_node", "__end__"]:
    print("---NODE: Router---")
    last_message = state["messages"][-1]
    
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        print("---Router: Rerouting to tools---")
        return "retriever_node"
    
    print("---Router: Routing to end---")
    return "__end__"


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

app = graph.compile()


def main():
    while True:
        user_input = input("User: ")
        
        if user_input.lower() in ["exit", "quit", "q"]:
            break
        
        inputs = {"messages": [HumanMessage(content=user_input)]}
        
        for event in app.stream(inputs, stream_mode="values"): #type: ignore
            pass 

        final_state = event #type: ignore
        final_message = final_state["messages"][-1]
        
        if isinstance(final_message, AIMessage):
            print(f"Assistant: {final_message.content}")
        else:
            print(f"Graph ended with: {final_message.pretty_print()}")


if __name__ == "__main__":
    main()