from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService

from dotenv import load_dotenv

load_dotenv()


embedding_service = EmbeddingService()

qdrant_service = QdrantService()

retrieval_service = RetrievalService(
    embedding_service=embedding_service,
    qdrant_service=qdrant_service,
)

llm_service = LLMService()

rag_service = RAGService(
    retrieval_service=retrieval_service,
    llm_service=llm_service,
)


response = rag_service.answer_question(
    query="¿Cómo se gestionan las vacaciones?"
)


print("Respuesta:")
print()
print(response.answer)

print()
print("Fuentes:")

for source in response.sources:

    print(
        f"- {source.filename} "
        f"(página {source.page_number})"
    )

print()
print(
    "¿Contexto suficiente?:",
    response.has_sufficient_context,
)