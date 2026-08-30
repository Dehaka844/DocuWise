from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
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
    ) -> list[SearchResult]:

        results = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_vector,
            limit=limit,
            with_payload=True,
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

