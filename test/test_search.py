from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService


embedding_service = EmbeddingService()

qdrant_service = QdrantService()


query = "¿Cuántos días de vacaciones tienen los empleados?"


query_embedding = embedding_service.embed_text(
    query
)


results = qdrant_service.search(
    query_vector=query_embedding,
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

    print(f"Resultado {index}")

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