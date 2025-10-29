import json
import operator
from typing import Annotated, Any, List, Literal, Optional, TypedDict

from backend.src.infrastructure.config.promtps import (DOC_GRADER_PROMPT, RAG_PROMPT,
                                           ROUTER_INSTRUCTION)
from langchain_core.documents import Document
from langchain_core.messages import (AIMessage, HumanMessage, SystemMessage,
                                     ToolMessage)
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.llm.llm import (
    get_llm, get_normal_llm)
from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.tools.doc_retriever_tool import \
    get_retriever_tool
from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.tools.search_tool import \
    search_web


# --- State ---
class State(TypedDict):
    query: str
    messages: Annotated[List[Any], add_messages]
    web_search: str
    doc_hash: Optional[str]
    documents: List[Document]
    search_results: Annotated[List[str], operator.add]
    

# 1. Retrieve node
def retrieve_node(state: State) -> State:
    """Retrieve documents based on the query."""
    print("==Retrieving documents...")
    query = state["query"]
    
    doc_hash = state.get("doc_hash", None)
    
    retriever_tool = get_retriever_tool(doc_hash=doc_hash)
    
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
    formatted_search = "\n".join(search_res for search_res in state["search_results"])
    
    docs_and_search = formatted_docs + "SEARCH RESULT: " + formatted_search 
    
    human_msg = HumanMessage(RAG_PROMPT.format(
        context=docs_and_search,
        question=query
    ))
    
    response = llm.invoke([human_msg])
    response = AIMessage(response.content)
    state["messages"].append(response)
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
    web_search_tool = search_web
    
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

# --- Main graph builder ---
def build_graph():
    graph = StateGraph(State)
    # add functionalities: retrieve, web_search, generate, grade_documents, only_greet
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("web_search", web_search_node)
    graph.add_node("generate", generate_node)
    graph.add_node("grade_documents", grade_documents_node)
    graph.add_node("only_greet", only_greet)
    
    # route the first question to the first node
    graph.set_conditional_entry_point(
        route_question,
        {
            "web_search": "web_search",
            "retrieve": "retrieve",
            'only_greet':'only_greet',
        }
    )
    # after retrieve, grade documents
    graph.add_edge("retrieve", "grade_documents")
    # after grading, decide to web_search or generate
    graph.add_conditional_edges(
        "grade_documents",
        decide_to_generate,
        {
            "web_search": "web_search",
            "generate": "generate",
        }
    )
    # after web_search, go to generate
    graph.add_edge("web_search", "generate")
    
    # these nodes lead to the end
    graph.add_edge("generate", END)
    graph.add_edge("only_greet", END)

    return graph.compile()















# for testting only
def main():
    print("Graph compiled. Multi-tool RAG agent ready.")
    app = build_graph()
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            break

        events = app.stream(
            {"query": user_input, "documents": [], "web_search": "yes", "messages": [], "doc_hash": None}, #type: ignore
            stream_mode="values",
        ) #type: ignore
        final_event = dict()
        
        for event in events:
            final_event = event
        final_event["messages"][-1].pretty_print()


if __name__ == "__main__":
    main()