import asyncio
import io

from fastapi import UploadFile

from app.ingestion.parsers.pdf_parser import PDFParser
from app.chunking.recursive_chunker import RecursiveChunker
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.services.ingestion_service import IngestionService


async def main():
    parser = PDFParser()

    chunker = RecursiveChunker()

    embedding_service = EmbeddingService()

    qdrant_service = QdrantService()

    ingestion_service = IngestionService(
        chunker=chunker,
        embedding_service=embedding_service,
        qdrant_service=qdrant_service,
    )

    pdf_path = (
        "./docs_example/"
        "Política Interna de Vacaciones y Organización del Trabajo.pdf"
    )

    with open(
        pdf_path,
        "rb",
    ) as file:
        file_content = file.read()

    upload_file = UploadFile(
        filename=(
            "Política Interna de Vacaciones y "
            "Organización del Trabajo.pdf"
        ),
        file=io.BytesIO(file_content),
    )

    document = await parser.parse(
        upload_file
    )

    result = ingestion_service.ingest(
        document
    )

    print(
        "Documento indexado correctamente"
    )

    print(
        f"Número de páginas: "
        f"{result.page_count}"
    )

    print(
        f"Número de chunks: "
        f"{result.chunk_count}"
    )

    print(
        f"Número de embeddings: "
        f"{result.embedding_count}"
    )

    print(
        f"Puntos almacenados: "
        f"{result.stored_points}"
    )


if __name__ == "__main__":
    asyncio.run(main())