from langchain_core.messages import AnyMessage
# from tools.search_tool import tavily_search
from tools.math_tools import add, multiply
from llm.cerebras_llm import get_llm
from typing_extensions import TypedDict, Annotated
import operator
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from prompts import SYSTEM_PROMPT
from typing import Literal
from langgraph.graph import StateGraph, END, START

class MessageState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int
        
# tools = [tavily_search, add, multiply]
tools = [add, multiply]

tools_by_name = {tool.name: tool for tool in tools}

llm = get_llm()
model_with_tools = llm.bind_tools(tools) 

def call_llm(state: dict):
    """LLM decides whether to call a tool or not"""
    
    return {
        "messages": [
            model_with_tools.invoke([
                SystemMessage(SYSTEM_PROMPT),
            ]
                + state["messages"]
            ),
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
    
def tool_node(state: dict):
    """Perform a tool call"""
    result = []
    
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call['name']]
        observation = tool.invoke(tool_call['args'])
        result.append(ToolMessage(
            content=str(observation),
            tool_call_id=tool_call['id']
        ))
    return {"messages":result}

def should_continue(state: MessageState) -> Literal["tool_node", END]: #type: ignore
    """Decide whether to continue or end the conversation."""
    messages = state["messages"]
    last_message = messages[-1]
    
    if last_message.tool_calls: #type: ignore
        return "tool_node"
    
    return END


graph = StateGraph(MessageState)

graph.add_node("llm_call", call_llm) #type: ignore
graph.add_node("tool_node", tool_node) #type: ignore

graph.add_edge(START, "llm_call")
graph.add_conditional_edges(
    "llm_call",
    should_continue,
    ["tool_node", END],
) 

app = graph.compile()

result = app.invoke({"messages": [HumanMessage("What is 2+2")], "llm_calls": 0})
print(result)