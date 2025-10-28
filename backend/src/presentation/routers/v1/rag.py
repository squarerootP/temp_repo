import os
import tempfile
from functools import lru_cache
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.src.application.use_cases.chat_ops.chat_with_specific_document import \
    ChatWithSpecificDocument
from backend.src.application.use_cases.chat_ops.context_aware_chat import \
    ChatWithPriorDocuments
from backend.src.application.use_cases.chat_ops.upload_doc import \
    DocumentUploaderAndProcessor
from backend.src.domain.entities.library_entities.user import User
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

# ----------------------------------------------------------
# Dependency Factories (cached for performance)
# ----------------------------------------------------------

@lru_cache()
def get_vector_repo() -> ChromaVectorStoreRepositoryImpl:
    """Singleton instance of the Chroma vectorstore."""
    return ChromaVectorStoreRepositoryImpl()


def get_chat_session_repo(db: Session = Depends(get_db)) -> ChatSessionRepositoryImpl:
    """Provides chat session repository per request."""
    return ChatSessionRepositoryImpl(db)


def get_rag_repo(
    vector_repo: ChromaVectorStoreRepositoryImpl = Depends(get_vector_repo),
    chat_repo: ChatSessionRepositoryImpl = Depends(get_chat_session_repo)
) -> LangGraphRAGRepositoryImpl:
    """Creates RAG repository with injected dependencies."""
    return LangGraphRAGRepositoryImpl(
        vector_repo=vector_repo,
        chat_repo=chat_repo,
    )


# ----------------------------------------------------------
# Router Setup
# ----------------------------------------------------------

router = APIRouter(
    prefix="/rag",
    tags=["RAG"]
)


# ----------------------------------------------------------
# 1️⃣ Chat with All Documents
# ----------------------------------------------------------

@router.post("/chat", response_model=ChatMessageResponse)
def chat_with_rag(
    chat_request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    rag_repo: LangGraphRAGRepositoryImpl = Depends(get_rag_repo),
    chat_repo: ChatSessionRepositoryImpl = Depends(get_chat_session_repo),
    role_check: None = Depends(has_role("admin")),
):
    """
    Chat with the RAG system using all prior documents.
    Only admins can access this endpoint.
    """
    chat_use_case = ChatWithPriorDocuments(
        rag_repo=rag_repo,
        chat_repo=chat_repo,
    )

    try:
        response_message = chat_use_case.generate_response(
            user_id=current_user.user_id,  # type: ignore
            session_id=chat_request.session_id, # type: ignore
            query=chat_request.content,
        )
        return response_message

    except UserNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal RAG error: {str(e)}")


# ----------------------------------------------------------
# 2️⃣ Chat with a Specific Document
# ----------------------------------------------------------

@router.post("/chat/document/{doc_hash}", response_model=ChatMessageResponse)
def chat_with_specific_document(
    doc_hash: str,
    chat_request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    rag_repo: LangGraphRAGRepositoryImpl = Depends(get_rag_repo),
    chat_repo: ChatSessionRepositoryImpl = Depends(get_chat_session_repo),
    vector_repo: ChromaVectorStoreRepositoryImpl = Depends(get_vector_repo),
    role_check: None = Depends(has_role("admin")),
):
    """
    Chat with the RAG system using a specific document (by hash).
    """
    # Validate document existence
    if doc_hash not in vector_repo.processed_documents:
        raise HTTPException(status_code=404, detail="Document not found in vectorstore")

    chat_use_case = ChatWithSpecificDocument(
        rag_repo=rag_repo,
        chat_session_repo=chat_repo,
        hash=doc_hash,
    )

    try:
        response_message = chat_use_case.generate_response(
            user_id=current_user.user_id,  # type: ignore
            session_id=chat_request.session_id, # type: ignore
            query=chat_request.content,
        )
        return response_message

    except UserNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal RAG error: {str(e)}")


# ----------------------------------------------------------
# 3️⃣ Upload & Process Document
# ----------------------------------------------------------

@router.post("/documents", status_code=status.HTTP_201_CREATED, response_model=DocumentUploadResponse)
async def upload_document_to_process(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    vector_repo: ChromaVectorStoreRepositoryImpl = Depends(get_vector_repo),
    role_check: None = Depends(has_role("admin")),
):
    """
    Upload a document to be processed and stored in the RAG system.
    Since the document is stored, only admin can access this endpoint.
    """
    await validate_uploaded_file(file) # validate size and extension
    
    doc_repo = DocumentRepositoryImpl(db=db, vector_repo=vector_repo)
    doc_use_case = DocumentUploaderAndProcessor(
        doc_repo=doc_repo,
        vector_repo=vector_repo,
    )

    _, ext = os.path.splitext(file.filename) # type: ignore
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext or ".txt") as temp_file: # use tempfile to store uploaded file
        temp_file.write(await file.read())
        temp_file_path = temp_file.name

    try:
        response_message = doc_use_case.ingest_document(temp_file_path, user_id = current_user.user_id) #type: ignore
        return DocumentUploadResponse(
            document_id=response_message.id,
            title=response_message.title,
            hash=response_message.hash, #type: ignore
            chunk_count=len(response_message.chunks),
            uploaded_at=response_message.uploaded_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)




@router.get("/documents", status_code=status.HTTP_200_OK)
def list_processed_documents(
    vector_repo: ChromaVectorStoreRepositoryImpl = Depends(get_vector_repo),
    role_check: None = Depends(has_role("admin")),
):
    """
    List all processed documents stored in the vector database.
    """
    return vector_repo.processed_documents

@router.get("/sessions/", response_model = List[ChatSessionResponse])
def get_user_sessions(
    current_user: User = Depends(get_current_user),
    chat_repo: ChatSessionRepositoryImpl = Depends(get_chat_session_repo)
) -> List[ChatSessionResponse]:
    try:
        sessions = chat_repo.get_sessions_by_user(user_id=current_user.user_id) # type: ignore
        return [ChatSessionResponse.model_validate(session) for session in sessions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve sessions: {str(e)}")
    
@router.get("/sessions/{session_id}", response_model = ChatSessionResponse)
def get_session_by_id(
    session_id: str,
    current_user: User = Depends(get_current_user),
    chat_repo: ChatSessionRepositoryImpl = Depends(get_chat_session_repo)
) -> ChatSessionResponse:
    
    
    try:
        if current_user.role != "admin":
            user_sessions = chat_repo.get_sessions_by_user(user_id=current_user.user_id) # type: ignore
            if session_id not in user_sessions:
                raise HTTPException(status_code=403, detail="Access denied to this session")
            
        # The following codes run if the user is admin or owns the session
        session = chat_repo.get_session_by_id(session_id=session_id) # type: ignore
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")
        return ChatSessionResponse.model_validate(session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session: {str(e)}")