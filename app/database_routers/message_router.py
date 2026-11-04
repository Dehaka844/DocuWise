from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database_models.user import User
from app.database_services.auth_dependency import get_current_user
from app.database_services.conversation_service import ConversationService
from app.database_services.message_service import MessageService

from app.database_models.message_request import MessageRequest
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService

from app.database_schemas.message_schema import (
    CreateMessageResponse,
    MessageResponse,
)

from app.exceptions.llm_exception import LLMServiceError


router = APIRouter(
    prefix="/conversations",
    tags=["Messages"],
)


@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageResponse],
)
def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation_service = ConversationService(db)

    conversation = conversation_service.get_conversation_by_id(
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversación no encontrada.",
        )

    message_service = MessageService(db)

    messages = message_service.get_conversation_messages(
        conversation_id=conversation_id,
    )

    return messages


@router.post(
    "/{conversation_id}/messages",
    response_model=CreateMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_message(
    conversation_id: int,
    request: MessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ---------------------------------------------------------
    # 1. Comprobar que la conversación pertenece al usuario
    # ---------------------------------------------------------

    conversation_service = ConversationService(db)

    conversation = conversation_service.get_conversation_by_id(
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversación no encontrada.",
        )

    # ---------------------------------------------------------
    # 2. Obtener el historial anterior
    # ---------------------------------------------------------

    message_service = MessageService(db)

    conversation_history = message_service.get_recent_messages(
        conversation_id=conversation_id,
        limit=10,
    )

    # ---------------------------------------------------------
    # 3. Guardar el mensaje del usuario
    # ---------------------------------------------------------

    user_message = message_service.create_message(
        conversation_id=conversation_id,
        role="user",
        content=request.content,
    )

    # ---------------------------------------------------------
    # 4. Crear servicios RAG
    # ---------------------------------------------------------

    embedding_service = EmbeddingService()

    qdrant_service = QdrantService()

    retrieval_service = RetrievalService(
        embedding_service=embedding_service,
        qdrant_service=qdrant_service,
    )

    llm_service = LLMService()

    rag_service = RAGService(
        retrieval_service=retrieval_service,
        llm_service=llm_service,
    )

    # ---------------------------------------------------------
    # 5. Ejecutar RAG utilizando el historial
    # ---------------------------------------------------------

    try:
        rag_response = rag_service.answer_question(
            query=request.content,
            limit=request.limit,
            conversation_history=conversation_history,
            user_id=current_user.id,
            departments=[department.code for department in current_user.departments],
            is_admin=current_user.role == "admin",
        )

    except LLMServiceError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "El servicio de generación de respuestas "
                "no está disponible en este momento."
            ),
        )

    # ---------------------------------------------------------
    # 6. Guardar la respuesta del asistente
    # ---------------------------------------------------------

    assistant_message = message_service.create_message(
        conversation_id=conversation_id,
        role="assistant",
        content=rag_response.answer,
        sources=rag_response.sources,
    )

    # ---------------------------------------------------------
    # 7. Devolver conversación + mensajes
    # ---------------------------------------------------------

    return {
        "user_message": user_message,
        "assistant_message": assistant_message,
        "sources": rag_response.sources,
        "has_sufficient_context": (
            rag_response.has_sufficient_context
        ),
    }
