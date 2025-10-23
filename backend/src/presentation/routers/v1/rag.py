from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.application.use_cases.chat_ops._chat_with_specific_document import \
    ChatWithSpecificDocument

from backend.src.application.use_cases.chat_ops._context_aware_chat import \
    ChatWithPriorDocuments
from backend.src.domain.entities.user import User
from backend.src.domain.exceptions.user_exceptions import UserNotFound
from backend.src.infrastructure.persistence.database import get_db
from backend.src.infrastructure.persistence.repository_impl._chat_session_repository_impl import \
    ChatSessionRepositoryImpl
from backend.src.infrastructure.persistence.repository_impl._document_repository_impl import \
    DocumentRepositoryImpl
from backend.src.infrastructure.persistence.repository_impl._vectorstore_repository_impl import \
    ChromaVectorStoreRepositoryImpl
from backend.src.infrastructure.persistence.repository_impl._rag_repository_impl import \
    LangGraphRAGRepositoryImpl
from backend.src.infrastructure.web.auth_provider import (get_current_user,
                                                          has_role)
from backend.src.presentation.schemas.chat_schema import (ChatRequestModel,
                                                          ChatResponseModel)
from backend.src.application.use_cases.chat_ops.a_rag_document_proc import DocumentProcessor

router = APIRouter(
    prefix="/rag", 
    tags=["RAG"]
)

@router.post("/chat", response_model = ChatResponseModel)
def chat_with_rag(
    chat_request: ChatRequestModel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    role_check: None = Depends(has_role("admin"))
):
    """
    Chat with RAG system using context-aware responses 
    using knowledge from all prior documents, meaning only admins can access this endpoint.
    """
    vector_repo = ChromaVectorStoreRepositoryImpl()
    embedding_repo = DocumentRepositoryImpl()
    chat_session_repo = ChatSessionRepositoryImpl(db)
    rag_repo = LangGraphRAGRepositoryImpl(
            embedding_repo=embedding_repo, 
            chat_repo=chat_session_repo)
    user_input = chat_request.message
    chat_use_cases = ChatWithPriorDocuments(rag_repo=rag_repo,
                                            chat_repo=chat_session_repo,)
    try:
        response_message = chat_use_cases.process_query(
            user_id=current_user.user_id, #type: ignore
            session_id=chat_request.session_id,
            query=user_input,
        )
    except UserNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    
    return response_message

@router.post("/chat/{doc_hash}", response_model= ChatResponseModel)
def chat_with_rag_specific_document(
    doc_hash: str,
    chat_request: ChatRequestModel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    role_check: None = Depends(has_role("admin"))
):
    """
    Chat with RAG system using a specific document identified by its hash.
    """
    vector_repo = ChromaVectorStoreRepositoryImpl()
    embedding_repo = ChromaDocumentRepository()
    chat_session_repo = ChatSessionRepositoryImpl(db)
    rag_repo = LangGraphRAGRepositoryImpl(vector_repo=vector_repo, 
    embedding_repo=embedding_repo, 
    chat_repo=chat_session_repo)
    user_input = chat_request.message
    doc_repo = DocumentRepositoryImpl()
    doc_processor = DocumentProcessor(doc_repo=doc_repo, vector_repo=vector_repo)
    chat_use_cases = ChatWithSpecificDocument(
        rag_repo=rag_repo,
        chat_repo=chat_session_repo,
        hash=doc_hash
    )
    try:
        response_message = chat_use_cases.process_query(
            user_id=current_user.user_id, #type: ignore
            session_id=chat_request.session_id,
            query=user_input,
        )
    except UserNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return response_message

@router.post("/document/process", status_code=status.HTTP_200_OK)
def upload_document_to_process(
    file: bytes,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    role_check: None = Depends(has_role("admin"))
):
    """
    Upload a document to be processed and added to the RAG system.
    """
    vector_repo = ChromaVectorStoreRepositoryImpl()
    embedding_repo = ChromaDocumentRepository()
    chat_session_repo = ChatSessionRepositoryImpl(db)
    rag_repo = LangGraphRAGRepositoryImpl(vector_repo=vector_repo, 
    embedding_repo=embedding_repo, 
    chat_repo=chat_session_repo)
    
    try:
        response_message = embedding_repo.process_and_add_document(file_bytes=file)
    except UserNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return response_message