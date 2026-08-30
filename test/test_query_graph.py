from app.graph.query_graph import QueryGraph

from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService

from dotenv import load_dotenv

load_dotenv()


embedding_service = EmbeddingService()

qdrant_service = QdrantService()

retrieval_service = RetrievalService(
    embedding_service=embedding_service,
    qdrant_service=qdrant_service,
)

llm_service = LLMService()

query_graph = QueryGraph(
    retrieval_service=retrieval_service,
    llm_service=llm_service,
)

graph = query_graph.build()


result = graph.invoke(
    {
        "query": "¿Cómo se gestionan las vacaciones?",
        "limit": 5,
    }
)

print(result["answer"])

print()
print(
    "¿Contexto suficiente?:",
    result["has_sufficient_context"],
)

print()
print("Respuesta:")
print()
print(result["answer"])

print()
print("Fuentes:")

for source in result["sources"]:

    print(
        f"- {source['filename']} "
        f"(página {source['page_number']})"
    )