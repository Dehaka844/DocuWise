from app.models.document import ParsedDocument
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.chunking.recursive_chunker import RecursiveChunker
from app.models.ingestion_result import IngestionResult


class IngestionService:

    def __init__(
        self,
        chunker: RecursiveChunker,
        embedding_service: EmbeddingService,
        qdrant_service: QdrantService,
    ):
        self.chunker = chunker

        self.embedding_service = (
            embedding_service
        )

        self.qdrant_service = (
            qdrant_service
        )

    def ingest(
        self,
        document: ParsedDocument,
    ) -> IngestionResult:

        chunks = (
            self.chunker.chunk_document(
                document
            )
        )

        texts = [
            chunk.content
            for chunk in chunks
        ]

        embeddings = (
            self.embedding_service.embed_texts(
                texts
            )
        )

        stored_points = (
            self.qdrant_service.upsert_chunks(
                chunks,
                embeddings,
            )
        )

        return IngestionResult(
            page_count=len(document.pages),
            chunk_count=len(chunks),
            embedding_count=len(embeddings),
            stored_points=stored_points,
        )