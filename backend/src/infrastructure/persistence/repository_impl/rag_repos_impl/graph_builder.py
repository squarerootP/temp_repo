import json
import operator
from typing import Annotated, Any, List, Literal, Optional, TypedDict

from langchain_core.documents import Document
from langchain_core.messages import (AIMessage, HumanMessage, SystemMessage,
                                     ToolMessage)
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from backend.src.application.interfaces.rag_interfaces.vectorstore_repo import \
    IVectorStoreRepository
from backend.src.infrastructure.config.promtps import (DOC_GRADER_PROMPT,
                                                       RAG_PROMPT,
                                                       ROUTER_INSTRUCTION)
from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.llm.llm import (
    get_big_llm, get_small_llm)
from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.tools.doc_retriever_tool import \
    get_retriever_tool
from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.tools.search_tool import \
    search_web
from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.vectorstore_repository_impl import \
    ChromaVectorStoreRepositoryImpl


# --- State ---
class State(TypedDict):
    query: str
    messages: Annotated[List[Any], add_messages]
    web_search: str
    document_hash: Optional[str]
    documents: List[Document]
    search_results: Annotated[List[str], operator.add]


# 1. Retrieve node
def retrieve_node(state: State, vector_repo: ChromaVectorStoreRepositoryImpl) -> State:
    """Retrieve documents based on the query."""
    print("==Retrieving documents...")

    query = state["query"]
    document_hash = state.get("document_hash", None)

    try:
        # Get documents from vector store
        if document_hash:
            docs_and_scores = (
                vector_repo.vectorstore.similarity_search_with_relevance_scores(  # type: ignore
                    query, k=6, filter={"document_hash": document_hash}
                )
            )
        else:
            docs_and_scores = (
                vector_repo.vectorstore.similarity_search_with_relevance_scores(  # type: ignore
                    query, k=6
                )
            )
        threshold = 0.7  # Adjust this threshold as needed
        relevant_docs = [doc for doc, score in docs_and_scores if score >= threshold]

        if relevant_docs:
            state["documents"].extend(relevant_docs)
            print(
                f"Retrieved {len(relevant_docs)} relevant documents (score >= {threshold})"
            )
            print(state["documents"])
        else:
            print("No documents met the relevance threshold")
            state["web_search"] = "yes"  # Fallback to web search

        print(f"Retrieved {len(state['documents'])} documents")
        print(
            "Sample document content:"
            + state["documents"][0].page_content[200:]
            + "..."
        )

    except Exception as e:
        print(f"Error retrieving documents: {e}")
        # Don't fail completely, just return state without documents

    return state


# 2. Generate node
def generate_node(state: State) -> State:
    """Generate final answer based on retrieved documents and web search if needed."""
    print("==Generating final answer...")
    big_llm = get_big_llm()
    query = state["query"]
    documents = state["documents"]
    formatted_docs = ""
    if documents:
        formatted_docs = "\n".join(doc.page_content for doc in documents)
    formatted_search = "\n".join(search_res for search_res in state["search_results"])

    docs_and_search = formatted_docs + "SEARCH RESULT: " + formatted_search

    human_msg = HumanMessage(RAG_PROMPT.format(context=docs_and_search, question=query))

    response = big_llm.invoke([human_msg])
    response = AIMessage(response.content)
    state["messages"].append(response)
    return state


# 3. Grade documents to update web_search flag
def grade_documents_node(state: State) -> State:
    """Decide whether web search is needed based on retrieved documents."""
    print("==Grading retrieved documents for relevance...")
    big_llm = get_big_llm()
    query = state["query"]
    documents = state["documents"]
    formatted_docs = "\n".join(doc.page_content for doc in documents)
    human = HumanMessage(
        DOC_GRADER_PROMPT.format(document=formatted_docs, question=query)
    )
    response = big_llm.invoke([human])
    response.pretty_print()
    web_search_decision = "no" if "yes" in response.content.strip().lower() else "yes"  # type: ignore
    state["web_search"] = web_search_decision
    return state


# 4. Web search node
def web_search_node(state: State) -> State:
    """Perform web search if needed."""
    web_search_tool = search_web

    print(f"==Performing web search...{state['web_search']}")

    if state["web_search"] == "yes":
        search_result = web_search_tool.invoke(state["query"])
        print(search_result)

        for item in search_result["results"]:
            cur_msg = item["content"]
            state["search_results"].append(cur_msg)

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
    small_llm = get_small_llm()
    query = state["query"]

    sysmes = SystemMessage(ROUTER_INSTRUCTION)
    human = HumanMessage(query)
    response = small_llm.invoke([sysmes, human])
    response.pretty_print()

    datasource = response.content.strip().lower()  # type: ignore
    if "web" in datasource or "search" in datasource:
        state["web_search"] = "yes"
        print("heading to web_search")
        return "web_search"
    elif "greet" in datasource:
        return "only_greet"
    else:
        return "retrieve"


def decide_to_generate(state: State) -> str:
    """Determine whether to generate or add web search"""
    web_search = state["web_search"]
    if web_search == "yes":
        return "web_search"
    else:
        return "generate"


def only_greet(state: State) -> State:
    """Generate a greeting response."""
    print("==Generating greeting response...")
    small_llm = get_small_llm()
    query = state["query"]

    human = HumanMessage(query)
    response = small_llm.invoke([human])
    response = AIMessage(response.content)
    state["messages"].append(response)
    return state


# --- Main graph builder ---
def build_graph(vector_repo: IVectorStoreRepository) -> StateGraph:
    graph = StateGraph(State)

    # add functionalities: retrieve, web_search, generate, grade_documents, only_greet
    def retrieve_with_repo(state: State) -> State:
        return retrieve_node(state, vector_repo)  # type: ignore

    graph.add_node("retrieve", retrieve_with_repo)
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
            "only_greet": "only_greet",
        },
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
        },
    )
    # after web_search, go to generate
    graph.add_edge("web_search", "generate")

    # these nodes lead to the end
    graph.add_edge("generate", END)
    graph.add_edge("only_greet", END)

    return graph.compile()  # type: ignore


# for testting only
def main():
    from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.vectorstore_repository_impl import \
        ChromaVectorStoreRepositoryImpl

    vector_repo = ChromaVectorStoreRepositoryImpl()
    app = build_graph(vector_repo)

    print("Graph compiled. Multi-tool RAG agent ready.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            break

        events = app.stream(  # type: ignore
            {
                "query": user_input,
                "documents": [],
                "web_search": "yes",
                "messages": [],
                "document_hash": None,
            },
            stream_mode="values",
        )

        final_event = dict()
        for event in events:
            final_event = event
        final_event["messages"][-1].pretty_print()


if __name__ == "__main__":
    main()
