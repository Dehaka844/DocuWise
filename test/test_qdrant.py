from app.services.qdrant_service import (
    QdrantService,
)


qdrant_service = QdrantService()

qdrant_service.ensure_collection()

print("Conexión con Qdrant correcta")
print(
    f"Colección: "
    f"{qdrant_service.COLLECTION_NAME}"
)
print(
    f"Dimensión vectorial: "
    f"{qdrant_service.VECTOR_SIZE}"
)