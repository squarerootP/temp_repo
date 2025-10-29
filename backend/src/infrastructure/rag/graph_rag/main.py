import json
import logging
import operator
import re
from typing import Annotated, TypedDict

from langchain_core.documents import Document
from langchain_core.messages import (AIMessage, AnyMessage, HumanMessage,
                                     SystemMessage, ToolMessage)
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel

# --- Import your modular components ---
from backend.src.infrastructure.rag.graph_rag.embedder.google_emb import \
    get_retriever_tool
from backend.src.infrastructure.rag.graph_rag.llm.llm import (get_llm,
                                                              get_normal_llm)
from backend.src.infrastructure.rag.graph_rag.prompts import (
    DOC_GRADER_PROMPT, RAG_PROMPT, ROUTER_INSTRUCTION)
from backend.src.infrastructure.rag.graph_rag.tools.tavily_search import \
    search_web

logging.getLogger("langchain").setLevel(logging.ERROR)

web_search_tool = search_web
retriever_tool = get_retriever_tool()

class State(TypedDict):
    """State contains information about the conversation."""
    query: str
    messages: Annotated[list[AnyMessage], add_messages]
    web_search: str
    documents: list[Document]
    search_results: Annotated[list[str], operator.add]


# 1. Retrieve node
def retrieve_node(state: State) -> State:
    """Retrieve documents based on the query."""
    print("==Retrieving documents...")
    query = state["query"]
    retrieval_result = retriever_tool.invoke(query)
    if isinstance(retrieval_result, list):
        state['documents'].extend(retrieval_result)
    elif isinstance(retrieval_result, Document):
        state['documents'].append(retrieval_result)
    else:
        raise ValueError("Incompatible formats")
    return state

# 2. Generate node
def generate_node(state: State) -> State:
    """Generate final answer based on retrieved documents and web search if needed."""
    print("==Generating final answer...")
    llm = get_normal_llm()
    query = state["query"]
    documents = state["documents"]
    formatted_docs = ""
    if documents:
        formatted_docs = "\n".join(doc.page_content for doc in documents)
    formatted_search = "\n".join(s for s in state['search_results'])
    formatted_docs += "SEARCH RESULT: " + formatted_search
    human = HumanMessage(RAG_PROMPT.format(
        context= formatted_docs,
        question=query
    ))
    response = llm.invoke([human])
    response = AIMessage(response.content)
    state['messages'].append(response)
    return state 

# 3. Grade documents to update web_search flag
def grade_documents_node(state: State) -> State:
    """Decide whether web search is needed based on retrieved documents."""
    print("==Grading retrieved documents for relevance...")
    llm = get_normal_llm()
    query = state["query"]
    documents = state["documents"]
    formatted_docs = "\n".join(doc.page_content for doc in documents)
    human = HumanMessage(DOC_GRADER_PROMPT.format(
        document=formatted_docs, 
        question=query
    ))
    response = llm.invoke([human])
    response.pretty_print()
    web_search_decision = "no" if response.content.strip().lower().startswith("yes") else "yes" # type: ignore
    state['web_search'] = web_search_decision
    return state 

# 4. Web search node
def web_search_node(state: State) -> State:
    """Perform web search if needed."""
    print(f"==Performing web search...{state['web_search']}")
    
    if state["web_search"] == "yes":
        search_result = web_search_tool.invoke(state["query"])
        print(search_result)
        
        for item in search_result['results']:
            cur_msg = item['content']
            state['search_results'].append(cur_msg)
        
        return state 
    return state

# 5. Route the initial question
def route_question(state: State) -> str:
    """
    Route question to websearch or RAG
    Args: 
        state (State): The current state containing the query.
    Returns:
        str: Next node to call ('web_search' or 'retrieve', or 'only_greet')
    """
    print("==Routing question to appropriate data source...")
    llm = get_llm()
    query = state["query"]
    
    sysmes = SystemMessage(ROUTER_INSTRUCTION)
    human = HumanMessage(query)
    response = llm.invoke([sysmes, human])
    response.pretty_print()
    
    route_data = json.loads(response.content) #type: ignore
    datasource = route_data.get("datasource", "vectorstore").lower()
    if datasource == "web_search":
        state['web_search'] = "yes"
        print("heading to web_search")
        return "web_search"
    elif datasource == "only_greet":
        return "only_greet"
    else:
        return "retrieve"

def decide_to_generate(state: State) -> str:
    """Determine whether to generate or add web search"""
    web_search = state['web_search']
    if web_search == "yes":
        return "web_search"
    else:
        return "generate"

def only_greet(state: State) -> State:
    """Generate a greeting response."""
    print("==Generating greeting response...")
    llm = get_normal_llm()
    query = state["query"]
    
    human = HumanMessage(query)
    response = llm.invoke([human])
    response = AIMessage(response.content)
    state['messages'].append(response) 
    return state 

graph = StateGraph(State)
graph.add_node("retrieve", retrieve_node)
graph.add_node("web_search", web_search_node)
graph.add_node("generate", generate_node)
graph.add_node("grade_documents", grade_documents_node)
graph.add_node("only_greet", only_greet)
graph.set_conditional_entry_point(
    route_question,
    {
        "web_search": "web_search",
        "retrieve": "retrieve",
        'only_greet':'only_greet',
    }
)
graph.add_edge("retrieve", "grade_documents")
graph.add_conditional_edges(
    'grade_documents',
    decide_to_generate,
    {
        "web_search": "web_search",
        "generate": "generate",        
    }

)
graph.add_edge("web_search", "generate")
graph.add_edge("generate", END)
app = graph.compile()

def main():
    print("Graph compiled. Multi-tool RAG agent ready.")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            break

        events = app.stream(
            {"query": user_input, "documents": [], "web_search": "yes", "messages": []}, #type: ignore
            stream_mode="values",
        ) #type: ignore
        final_event = dict()
        
        for event in events:
            final_event = event
        final_event["messages"][-1].pretty_print()


if __name__ == "__main__":
    main()