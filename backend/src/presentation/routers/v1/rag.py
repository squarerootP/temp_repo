import os
import tempfile
from functools import lru_cache
from typing import List, Optional

from fastapi import (APIRouter, Depends, File, HTTPException, Query,
                     UploadFile, status)
from sqlalchemy.orm import Session

from backend.src.application.use_cases._rag_ops.chat_with_context import \
    ChatWithContext
from backend.src.application.use_cases._rag_ops.get_all_processed_docs import \
    GetAllProcessedDocsUseCase
from backend.src.application.use_cases._rag_ops.get_session import \
    get_session_history
from backend.src.application.use_cases._rag_ops.upload_doc import \
    AddAndProcessDocument
from backend.src.domain.entities.library_entities.user import User
from backend.src.domain.exceptions.chat_exceptions import *
from backend.src.domain.exceptions.chat_exceptions import (
    ChatHistoryNotFound, NotAuthorizedToViewSession)
from backend.src.domain.exceptions.user_exceptions import UserNotFound
from backend.src.infrastructure.persistence.database import get_db
from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.chat_session_repository_impl import \
    ChatSessionRepositoryImpl
from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.document_repository_impl import \
    DocumentRepositoryImpl
from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.rag_repository_impl import \
    LangGraphRAGRepositoryImpl
from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.vectorstore_repository_impl import \
    ChromaVectorStoreRepositoryImpl
from backend.src.infrastructure.web.auth_provider import (get_current_user,
                                                          has_role)
from backend.src.infrastructure.web.file_validator import \
    validate_uploaded_file
from backend.src.presentation.schemas.rag_schemas.chat_schema import (
    ChatMessageRequest, ChatMessageResponse, ChatResponse, ChatSessionRequest,
    ChatSessionResponse)
from backend.src.presentation.schemas.rag_schemas.document_schema import \
    DocumentUploadResponse

from backend.src.infrastructure.web.dependencies import (
    get_chat_session_repo, get_rag_repo, get_vector_repo,)



router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Not authorized"},
        500: {"description": "Internal server error"},
    },
)


### CHAT WITH CONTEXT ENDPOINT, THIS MIGHT RECEIVE AND OPTIONAL HASH PARAMETER ###
@router.post("/chat", response_model=ChatMessageResponse)
def chat_with_context(
    chat_request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    rag_repo: LangGraphRAGRepositoryImpl = Depends(get_rag_repo),
    chat_repo: ChatSessionRepositoryImpl = Depends(get_chat_session_repo),
    hash: Optional[str] = Query(None, description="Optional document hash"),
):
    """
    This chat can be triggered in two modes:
    1: General chat (this uses all embedded content in the vectorstore, including all books)
    2. With hash, this is applied when you're on a specific book page, the hash will be determined by the frontend
    What you can do?
    
     - chat about book(s)
     - Asking for book recommendation
     - Book search based on criteria
    """
    chat_with_context_use_case = ChatWithContext(
        rag_repo=rag_repo, chat_session_repo=chat_repo, hash=hash
    )
    try:
        response_message = chat_with_context_use_case.generate_response(
            current_user=current_user,
            session_id=chat_request.session_id,  # type: ignore
            query=chat_request.content,
            hash=hash,
        )
        return response_message

    except UserNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal RAG error: {str(e)}")


### UPLOAD DOCUMENT, THIS WILL GO INTO THE VECTORSTORE AND THE NORMAL DB###
@router.post(
    "/documents",
    status_code=status.HTTP_201_CREATED,
    response_model=DocumentUploadResponse,
    dependencies=[Depends(has_role("admin"))],
)
async def upload_document_to_process(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    vector_repo: ChromaVectorStoreRepositoryImpl = Depends(get_vector_repo),
):
    """
    Upload a document to be processed and stored in the RAG system.
    Since the document is stored, only admin can access this endpoint.
    """
    await validate_uploaded_file(file)  # validate size and extension

    doc_repo = DocumentRepositoryImpl(db=db)

    upload_doc_use_case = AddAndProcessDocument(
        doc_repo=doc_repo,
        vector_repo=vector_repo,
    )
    original_filename = file.filename  # Store original filename
    _, ext = os.path.splitext(file.filename)  # type: ignore
    
    if not ext:
        raise HTTPException(
            status_code=400, detail="File might be corrupted or has no extension."
        )
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=ext
    ) as temp_file:  # use tempfile to store uploaded file
        temp_file.write(await file.read())
        temp_file_path = temp_file.name

    try:
        response_message = upload_doc_use_case.add_documents(
            file_path=temp_file_path, 
            user_id=current_user.user_id, # type: ignore
            file_name=original_filename, # type: ignore
        )  
        return DocumentUploadResponse(
            book_isbn=response_message.book_isbn,
            title=response_message.title,
            hash=response_message.hash, #type: ignore 
        )
    except DocumentAlreadyProcessed as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process document: {str(e)}"
        )
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


### LIST ALL PROCESSED DOCUMENTS IN VECTORSTORE ###
@router.get("/documents", status_code=status.HTTP_200_OK)
def list_processed_documents_hashes(
    vector_repo: ChromaVectorStoreRepositoryImpl = Depends(get_vector_repo),
    role_check: None = Depends(has_role("admin")),
):
    """
    List all processed documents stored in the vector database.
    """
    processed_docs = GetAllProcessedDocsUseCase(vectorstore_repo=vector_repo).execute()
    print(processed_docs)

    return processed_docs


@router.get("/sessions/", response_model=List[ChatSessionResponse])
def get_user_sessions(
    current_user: User = Depends(get_current_user),
    chat_repo: ChatSessionRepositoryImpl = Depends(get_chat_session_repo),
) -> List[ChatSessionResponse]:
    try:
        sessions = chat_repo.get_sessions_by_user(user_id=current_user.user_id)  # type: ignore
        return [ChatSessionResponse.model_validate(session) for session in sessions]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve sessions: {str(e)}"
        )


### GET SESSION BY ID ENDPOINT ###
@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
def get_session_by_id(
    session_id: str,
    current_user: User = Depends(get_current_user),
    chat_repo: ChatSessionRepositoryImpl = Depends(get_chat_session_repo),
) -> ChatSessionResponse:
    try:
        session = get_session_history(
            user=current_user, session_id=session_id, chat_repo=chat_repo
        )
        return ChatSessionResponse.model_validate(session)
    except NotAuthorizedToViewSession:
        raise HTTPException(
            status_code=403, detail="Not authorized to view this session"
        )
    except ChatHistoryNotFound:
        raise HTTPException(status_code=404, detail="Chat history not found")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve session: {str(e)}"
        )

