from fastapi import APIRouter, Depends, HTTPException, status

from app.models.query_request import QueryRequest
from app.models.rag_response import RAGResponse

from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService

from app.exceptions.llm_exception import LLMServiceError
from app.database_models.user import User
from app.database_services.auth_dependency import get_current_user


router = APIRouter(
    prefix="/query",
    tags=["query"],
)


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


@router.post(
    "/",
    response_model=RAGResponse,
)
def query_documents(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
):

    try:

        response = rag_service.answer_question(
            query=request.query,
            limit=request.limit,
            user_id=current_user.id,
            departments=[department.code for department in current_user.departments],
            is_admin=current_user.role == "admin",
        )

        return response

    except LLMServiceError:

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "El servicio de generación de respuestas "
                "no está disponible en este momento."
            ),
        )

    return response
