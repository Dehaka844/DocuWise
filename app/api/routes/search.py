from fastapi import APIRouter, Depends

from app.database_models.user import User
from app.database_services.auth_dependency import get_current_user

from app.models.search_request import SearchRequest
from app.models.search_response import SearchResponse

from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.services.retrieval_service import RetrievalService


router = APIRouter(
    prefix="/search",
    tags=["search"],
)


embedding_service = EmbeddingService()

qdrant_service = QdrantService()

retrieval_service = RetrievalService(
    embedding_service=embedding_service,
    qdrant_service=qdrant_service,
)


@router.post(
    "/",
    response_model=SearchResponse,
)
def search_documents(
    request: SearchRequest,
    current_user: User = Depends(get_current_user),
):

    results = retrieval_service.retrieve(
        query=request.query,
        limit=request.limit,
        user_id=current_user.id,
        departments=[department.code for department in current_user.departments],
        is_admin=current_user.role == "admin",
    )

    return SearchResponse(
        query=request.query,
        results=results,
    )
