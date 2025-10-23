from pydantic import BaseModel


class ChatRequestModel(BaseModel):
    session_id: str
    user_input: str
    message: str
    thread_id: str = "1"

class ChatResponseModel(BaseModel):
    user_input: str
    response: str
    thread_id: str