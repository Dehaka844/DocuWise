from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.services.retrieval_service import RetrievalService


embedding_service = EmbeddingService()

qdrant_service = QdrantService()

retrieval_service = RetrievalService(
    embedding_service=embedding_service,
    qdrant_service=qdrant_service,
)


query = (
    "¿Cuántos días de vacaciones "
    "tienen los empleados?"
)


results = retrieval_service.retrieve(
    query=query,
    limit=5,
)


print(f"Pregunta: {query}")

print()

print("Resultados:")


for index, result in enumerate(
    results,
    start=1,
):
    print()

    print(
        f"Resultado {index}"
    )

    print(
        f"Score: {result.score}"
    )

    print(
        f"Página: "
        f"{result.metadata.get('page_number')}"
    )

    print(
        "Contenido:"
    )

    print(
        result.content
    )

    print("-" * 80)