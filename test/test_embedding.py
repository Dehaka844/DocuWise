import asyncio
import io

from fastapi import UploadFile

from app.ingestion.parsers.pdf_parser import PDFParser
from app.chunking.recursive_chunker import RecursiveChunker
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService


async def main():
    parser = PDFParser()

    chunker = RecursiveChunker()

    embedding_service = EmbeddingService()

    qdrant_service = QdrantService()

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

    document = await parser.parse(upload_file)

    chunks = chunker.chunk_document(document)

    texts = [
        chunk.content
        for chunk in chunks
    ]

    embeddings = embedding_service.embed_texts(
        texts
    )

    stored_points = qdrant_service.upsert_chunks(
        chunks,
        embeddings,
    )

    print("Documento procesado correctamente")

    print(
        f"Número de páginas: "
        f"{len(document.pages)}"
    )

    print(
        f"Número de chunks: "
        f"{len(chunks)}"
    )

    print(
        f"Número de embeddings: "
        f"{len(embeddings)}"
    )

    if embeddings:
        print(
            f"Dimensiones del primer embedding: "
            f"{len(embeddings[0])}"
        )

    print(
        f"Puntos almacenados en Qdrant: "
        f"{stored_points}"
    )


if __name__ == "__main__":
    asyncio.run(main())