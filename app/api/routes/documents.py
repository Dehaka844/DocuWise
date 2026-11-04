from uuid import uuid4

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Response, status, UploadFile
from sqlalchemy.orm import Session

from app.database_services.auth_dependency import get_current_admin
from app.database_models.user import User
from app.database.connection import get_db
from app.services.document_service import DocumentService
from app.database_services.user_service import UserService

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
    visibility: str = Form(...),
    allowed_departments: list[str] = Form(default=[]),
    owner_user_id: int | None = Form(default=None),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    valid_departments = {"rrhh", "tecnico", "marketing"}

    if visibility not in {"all", "departments", "personal"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La visibilidad del documento no es válida.",
        )

    if not set(allowed_departments).issubset(valid_departments):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La lista contiene un departamento no válido.",
        )

    if visibility == "departments" and not allowed_departments:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Selecciona al menos un departamento autorizado.",
        )

    if visibility == "personal" and owner_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Selecciona el usuario propietario del documento.",
        )

    if owner_user_id is not None:
        owner = UserService(db).get_user_by_id(owner_user_id)
        if owner is None or not owner.is_active:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El propietario debe ser un usuario activo existente.",
            )

    if visibility != "personal" and owner_user_id is not None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Solo los documentos personales pueden tener propietario.",
        )

    if visibility == "all":
        domains = ["general"]
    elif visibility == "departments":
        domains = sorted(set(allowed_departments))
    else:
        domains = sorted(set(["datos_personales", *allowed_departments]))

    metadata = {
        "document_id": str(uuid4()),
        "domains": domains,
        "visibility": visibility,
        "allowed_departments": sorted(set(allowed_departments)),
        "allowed_user_ids": [owner_user_id] if owner_user_id is not None else [],
    }
    chunks = await document_service.process_and_chunk_document(
        file,
        extra_metadata=metadata,
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


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    filename: str = Query(
        min_length=1,
        description="Nombre completo del archivo, incluida su extensión.",
    ),
    current_admin: User = Depends(get_current_admin),
) -> Response:
    qdrant_service.delete_document(filename)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
