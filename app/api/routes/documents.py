from fastapi import APIRouter, UploadFile

from app.services.document_service import DocumentService


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


document_service = DocumentService()


@router.post("/")
async def upload_document(
    file: UploadFile,
):

    chunks = await document_service.process_and_chunk_document(
        file
    )

    return {
        "filename": file.filename,
        "chunk_count": len(chunks),
        "chunks": [
            {
                "index": chunk.metadata["chunk_index"],
                "page_number": chunk.metadata["page_number"],
                "content_length": len(chunk.content),
                "content_preview": chunk.content[:200],
                "content_end_preview": chunk.content[-200:],
            }
            for chunk in chunks
        ],
    }