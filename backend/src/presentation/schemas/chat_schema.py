from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    thread_id: str = "1"

class ChatResponse(BaseModel):
    response: str
    thread_id: str