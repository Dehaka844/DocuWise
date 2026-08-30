from app.models.search_result import SearchResult
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService


class RetrievalService:

    def __init__(
        self,
        embedding_service: EmbeddingService,
        qdrant_service: QdrantService,
    ):
        self.embedding_service = embedding_service
        self.qdrant_service = qdrant_service

    def retrieve(
        self,
        query: str,
        limit: int = 5,
    ) -> list[SearchResult]:

        query_embedding = (
            self.embedding_service.embed_text(
                query
            )
        )

        results = self.qdrant_service.search(
            query_vector=query_embedding,
            limit=limit,
        )

        return results