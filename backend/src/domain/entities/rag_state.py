from typing import Annotated, List

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class ChatState(TypedDict):
    """State for the RAG chat system"""
    messages: Annotated[List[BaseMessage], add_messages]
    name: str
    birthday: str
