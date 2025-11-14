import json
import operator
from typing import Annotated, Any, Dict, List, Literal, Optional, TypedDict

from langchain_core.documents import Document
from langchain_core.messages import (AIMessage, HumanMessage, SystemMessage,
                                     ToolMessage)
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from backend.src.application.interfaces.rag_interfaces.vectorstore_repo import \
    IVectorStoreRepository
from backend.src.infrastructure.config.promtps import (DOC_GRADER_PROMPT,
                                                       RAG_PROMPT,
                                                       ROUTER_INSTRUCTION,
                                                       FIELDS_EXTRACTION_PROMPT,
                                                       GENERATE_AFTER_FIND_BOOKS_PROMPT)
from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.llm.llm import (
    get_big_llm, get_small_llm, get_field_extractor_llm)
from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.tools.doc_retriever_tool import \
    get_retriever_tool
from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.tools.search_tool import \
    search_web
from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.vectorstore_repository_impl import \
    ChromaVectorStoreRepositoryImpl
from backend.src.infrastructure.config.settings import rag_settings
from backend.src.infrastructure.persistence.repository_impl.library_repos_impl.book_repository_impl import BookRepositoryImpl
from backend.src.application.interfaces.library_interfaces.book_repository import BookRepository
from datetime import datetime
from backend.src.domain.entities.library_entities.book import Book
from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.tools.doc_retriever_tool import \
    get_embedding_function
import re

def parse_model_json(content: str) -> Optional[Dict[str, Any]]:
    """
    Safely parse a JSON string returned by a model, handling optional ```json``` code blocks.
    
    Args:
        content (str): The raw string from the model.
        
    Returns:
        dict: Parsed JSON as Python dictionary, or None if parsing fails.
    """
    if not content:
        return None

    # Remove ```json ... ``` or ``` ... ``` if present
    clean_content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content, flags=re.DOTALL).strip()
    
    try:
        return json.loads(clean_content)
    except json.JSONDecodeError:
        # If JSON parsing fails, return None (or you could log/raise an error)
        return None
    
# --- State ---
class State(TypedDict):
    query: str
    messages: Annotated[List[Any], add_messages]
    web_search: str
    document_hash: Optional[str]
    documents: List[Document]
    search_results: Annotated[List[str], operator.add]
    books_list: List[Book]

## ROUTING THE FIRST NODE
def route_question(state: State) -> str:
    """
    Route question to websearch or RAG
    Args:
        state (State): The current state containing the query.
    Returns:
        str: Next node to call ('web_search' or 'retrieve', or 'only_greet' or "find_books")
    """
    print("==Routing question to appropriate data source...")
    small_llm = get_small_llm()
    query = state["query"]

    sysmes = SystemMessage(ROUTER_INSTRUCTION)
    human = HumanMessage(query)
    response = small_llm.invoke([sysmes, human])
    response.pretty_print()

    datasource = response.content.strip().lower()  # type: ignore
    if "find" in datasource or "find_books" in datasource or "recommend" in datasource:
        return "find_books"
    elif "web" in datasource or "search" in datasource:
        state["web_search"] = "yes"
        print("heading to web_search")
        return "web_search"
    elif "greet" in datasource:
        return "only_greet"
    elif "vectorstore" in datasource:
        return "retrieve"
    else:
        print(f"Unexpected routing response: {datasource}. Defaulting to web_search")
        state["web_search"] = "yes"
        return "web_search"

# ===============                                                 ===============
#                  ROUTE -> FIND BOOKS -> GENERATE FINAL ANSWER 
# ===============                                                 ===============
# 1: Find books (extract fields then filter based on fields and semantic search on summary)
def find_books_node(state: State, books_repo: BookRepository, vector_repo: ChromaVectorStoreRepositoryImpl) -> State:
    big_llm = get_field_extractor_llm()
    query = state["query"]

    author_list = books_repo.get_all_authors()
    genre_list = books_repo.get_all_genres()

    human_msg = HumanMessage(FIELDS_EXTRACTION_PROMPT.format(
        authors_list=", ".join(author_list),
        valid_genres_list=", ".join(genre_list),
        user_query=query,
        current_date=datetime.now().strftime("%Y-%m-%d")
    ))

    response = big_llm.invoke([human_msg])
    print(response)
    response_content = parse_model_json(response.content)
    # output = json.loads(response_content)
    output = response_content   
    filtered_book_list = books_repo.get_books_with_filter(
        genre=output.get("Genre", None), 
        author=output.get("Author", None),
        title=output.get("Title", None),
        published_year=output.get("Publication Year", None),
        )
    matching_book_list = filtered_book_list
    
    if summary := output.get("Summary", None):
        # emb_summary = get_embedding_function().embed_query(summary)
        print("Performing sim search")
        matched_docs = vector_repo.get_similar_chunks(summary, rag_settings.NUM_DOCS_RETRIEVED, "summary_chunks")
        matched_book_isbns = set()
        print()
        for doc in matched_docs:
            print(doc)
            if "book_isbn:" in doc.metadata:
                matched_book_isbns.add(doc.metadata["book_isbn:"])
        
        matching_isbns = {book.book_isbn for book in matching_book_list}

        for book_isbn in matched_book_isbns:
            if book_isbn not in matching_isbns:
                book = books_repo.get_book_by_isbn(book_isbn)
                if book:
                    matching_book_list.append(book)
                    matching_isbns.add(book_isbn)
        ## This is stricter way, taking intersection
        # matching_book_list = [book for book in filtered_book_list if book.book_isbn in matched_book_isbns]
        # This is less strict, concatenating all
        # matching_book_list.extend(matched_docs)
    
    state["books_list"] = matching_book_list
    
    return state

# 2. Generate from the matching books, heading to END
def generate_after_find_books_node(state: State) -> State:
    """Generate final answer after finding books."""
    print("==Generating final answer after finding books...")
    big_llm = get_big_llm()
    query = state["query"]
    book_status = state['books_list']
    print(f"here are the books found: {[book.title for book in book_status]}")
    
    if not state['books_list']:
        book_status = "No books found matching the criteria."
        
    human_msg = HumanMessage(GENERATE_AFTER_FIND_BOOKS_PROMPT.format(
                                user_query=query, 
                                books_list=book_status)
                             )
    response = big_llm.invoke([human_msg])
    response = AIMessage(response.content)
    
    state["messages"].append(response)
    return state

# ===============                                                 ===============
#                 ROUTE -> DOCUMENT RETRIEVAL -> GRADE DOCUMENTS -> 
#                 (WEB SEARCH IF NEEDED) -> GENERATE FINAL ANSWER 
# ===============                                                 ===============
# 1. Retrieve documents 
def retrieve_node(state: State, vector_repo: ChromaVectorStoreRepositoryImpl) -> State:
    """Retrieve documents based on the query."""
    print("==Retrieving documents...")

    query = state["query"]
    document_hash = state.get("document_hash", None)

    try:
        
        filter_dict = {"document_hash": document_hash} if document_hash else None

        relevant_docs = vector_repo.get_similar_chunks(query=query, k=rag_settings.NUM_DOCS_RETRIEVED, filter_dict=filter_dict)

        if relevant_docs:
            state['documents'] = [doc for doc in relevant_docs]
            print(f"retrieved {len(relevant_docs)} documents.")
            print(state['documents'][0].page_content[:100]+ "...")
        else:
            print("No relevant documents found above the threshold.")
            state["web_search"] = "yes"  # fallback to web search

    except Exception as e:
        print(f"Error retrieving documents: {e}")
        state["web_search"] = "yes"
        
    return state

# 2. Grade document to determine whether to search, the flag means whether the documents are sufficient 
# "yes" (document is sufficient) -> "no" (doesn't need web_search), vice versa
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

def decide_to_generate(state: State) -> str:
    """Determine whether to generate or add web search"""
    web_search = state["web_search"]
    if web_search == "yes":
        return "web_search"
    else:
        return "generate"
    
# 3. Web search node (this is performed if documents are sufficient)
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

# ===============                                                 ===============
#                  ROUTE -> ONLY_GREET -> GENERATE FINAL ANSWER 
# ===============                                                 ===============
def only_greet(state: State) -> State:
    """Generate a greeting response."""
    print("==Generating greeting response...")
    small_llm = get_small_llm()
    query = state["query"]

    human = HumanMessage(query)
    response = small_llm.invoke([human])
    ai_response = AIMessage(response.content)
    state["messages"].append(ai_response)  # Add this line
    return state

# ===============                                                 ===============
#                          THE FINAL GENERATE ANSWER NODE 
# ===============                                                 ===============
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


# --- Main graph builder ---
def build_graph(vector_repo: IVectorStoreRepository, books_repo: BookRepository) -> StateGraph:
    graph = StateGraph(State)

    # add functionalities: retrieve, web_search, generate, grade_documents, only_greet, find_books
    def retrieve_with_repo(state: State) -> State:
        return retrieve_node(state, vector_repo)  # type: ignore

    graph.add_node("retrieve", retrieve_with_repo)
    graph.add_node("web_search", web_search_node)
    graph.add_node("generate", generate_node)
    graph.add_node("grade_documents", grade_documents_node)
    graph.add_node("only_greet", only_greet)

    def find_books_with_repos(state: State) -> State:
        return find_books_node(state, books_repo, vector_repo)  # type: ignore
    
    graph.add_node("find_books", find_books_with_repos)
    graph.add_node("generate_after_find_books", generate_after_find_books_node)
    # route the first question to the first node
    graph.set_conditional_entry_point(
        route_question,
        {
            "find_books": "find_books",
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
    # after find_books, go to generate
    graph.add_edge("find_books", "generate_after_find_books")
    
    # these nodes lead to the end
    graph.add_edge("generate", END)
    graph.add_edge("only_greet", END)
    graph.add_edge("generate_after_find_books", END)
    return graph.compile()  # type: ignore



