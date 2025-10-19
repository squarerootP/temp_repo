import json
from typing import AsyncIterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from backend.src.application.use_cases.chat_ops.chat import ChatInteraction
from backend.src.infrastructure.rag.graph_service import LangGraphRAGService
from backend.src.presentation.schemas.rag_schema import (ChatRequest,
                                                         ChatResponse)

router = APIRouter(prefix="/rag", tags=["RAG (dev)"])

def get_rag_service():
    # Dev-only service
    return LangGraphRAGService()

def get_chat_interaction(rag_service=Depends(get_rag_service)):
    return ChatInteraction(rag_service)

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    chat_interaction: ChatInteraction = Depends(get_chat_interaction)
):
    response = ""
    async for event in chat_interaction.execute(request.message, request.thread_id):
        if "messages" in event:
            last_msg = event["messages"][-1]
            if hasattr(last_msg, "content") and getattr(last_msg, "type", "") == "ai":
                response = last_msg.content
    return ChatResponse(response=response, thread_id=request.thread_id)

@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    chat_interaction: ChatInteraction = Depends(get_chat_interaction)
):
    async def event_generator() -> AsyncIterator[str]:
        async for event in chat_interaction.execute(request.message, request.thread_id):
            yield f"data: {json.dumps(event, default=str)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")