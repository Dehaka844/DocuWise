from fastapi import APIRouter, UploadFile

from app.services.document_service import DocumentService

from app.chunking.recursive_chunker import RecursiveChunker
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.services.ingestion_service import IngestionService


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

chunker = RecursiveChunker()

embedding_service = EmbeddingService()

qdrant_service = QdrantService()

ingestion_service = IngestionService(
    chunker=chunker,
    embedding_service=embedding_service,
    qdrant_service=qdrant_service,
)

document_service = DocumentService()


@router.post("/")
async def upload_document(
    file: UploadFile,
):
    chunks = await document_service.process_and_chunk_document(
        file
    )

    texts = [
        chunk.content
        for chunk in chunks
    ]

    embeddings = embedding_service.embed_texts(
        texts
    )

    stored_points = qdrant_service.upsert_chunks(
        chunks=chunks,
        embeddings=embeddings,
    )

    return {
        "filename": file.filename,
        "chunk_count": len(chunks),
        "embedding_count": len(embeddings),
        "stored_points": stored_points,
    }