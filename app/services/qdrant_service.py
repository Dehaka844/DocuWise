from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    FilterSelector,
    MatchValue,
    MatchAny,
    PointStruct,
    VectorParams,
)

from app.models.document import DocumentChunk
from app.models.search_result import SearchResult


class QdrantService:

    COLLECTION_NAME = "document_chunks"

    VECTOR_SIZE = 384

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
    ):
        self.client = QdrantClient(
            host=host,
            port=port,
        )

    def ensure_collection(
        self,
    ) -> None:

        if self.client.collection_exists(
            self.COLLECTION_NAME
        ):
            return

        self.client.create_collection(
            collection_name=self.COLLECTION_NAME,
            vectors_config=VectorParams(
                size=self.VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )

    def upsert_chunks(
        self,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
    ) -> int:

        self.ensure_collection()

        if len(chunks) != len(embeddings):
            raise ValueError(
                "The number of chunks must match "
                "the number of embeddings"
            )

        points = []

        for chunk, embedding in zip(
            chunks,
            embeddings,
        ):

            point = PointStruct(
                id=str(uuid4()),
                vector=embedding,
                payload={
                    "content": chunk.content,
                    **chunk.metadata,
                },
            )

            points.append(point)

        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=points,
        )

        return len(points)

    def search(
        self,
        query_vector: list[float],
        limit: int = 5,
        user_id: int | None = None,
        departments: list[str] | None = None,
        is_admin: bool = False,
    ) -> list[SearchResult]:

        access_filter = None
        if not is_admin:
            visible_conditions = [
                FieldCondition(
                    key="visibility",
                    match=MatchValue(value="all"),
                ),
            ]

            if departments:
                visible_conditions.append(
                    FieldCondition(
                        key="allowed_departments",
                        match=MatchAny(any=departments),
                    )
                )

            if user_id is not None:
                visible_conditions.append(
                    FieldCondition(
                        key="allowed_user_ids",
                        match=MatchValue(value=user_id),
                    )
                )

            access_filter = Filter(should=visible_conditions)

        results = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_vector,
            limit=limit,
            with_payload=True,
            query_filter=access_filter,
        ).points

        search_results = []

        for result in results:

            payload = result.payload

            content = payload.get(
                "content",
                "",
            )

            metadata = {
                key: value
                for key, value in payload.items()
                if key != "content"
            }

            search_result = SearchResult(
                content=content,
                score=result.score,
                metadata=metadata,
            )

            search_results.append(search_result)

        return search_results

    def delete_document(
        self,
        filename: str,
    ) -> None:

        if not self.client.collection_exists(
            self.COLLECTION_NAME
        ):
            return

        filename_filter = Filter(
            must=[
                FieldCondition(
                    key="filename",
                    match=MatchValue(value=filename),
                )
            ]
        )

        self.client.delete(
            collection_name=self.COLLECTION_NAME,
            points_selector=FilterSelector(
                filter=filename_filter,
            ),
            wait=True,
        )

