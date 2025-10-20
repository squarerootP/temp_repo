from typing import Annotated

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.types import Command, interrupt


@tool
def human_assistance(
    name: str,
    birthday: str,
    tool_call_id: Annotated[str, InjectedToolCallId]) -> str:
    
    "Request human assistance from a human "
    "if the chatbot thinks he/she cannot answer the question by his/herself"

    human_response = interrupt({
        "question":"Is this correct?",
        "name": name,
        "birthday": birthday
        }
    )
    if human_response.get("correct", "").lower().startswith("y"):
        verified_name = name
        verified_birthday = birthday
        response = "Corerct"
    else:
        verified_name = human_response.get("name", name)
        verified_birthday = human_response.get("birthday", birthday)
        response = f"Made a correction: {human_response}"

    state_update = {
        "name" : verified_name,
        "birthday" : verified_birthday,
        "messages": [ToolMessage(content=response, tool_call_id=tool_call_id)]
    }
    return Command(update=state_update)


