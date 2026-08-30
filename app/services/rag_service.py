from app.graph.query_graph import QueryGraph

from app.models.rag_response import RAGResponse

from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService


class RAGService:

    def __init__(
        self,
        retrieval_service: RetrievalService,
        llm_service: LLMService,
    ):

        self.query_graph = QueryGraph(
            retrieval_service=retrieval_service,
            llm_service=llm_service,
        )

        self.graph = self.query_graph.build()


    def answer_question(
        self,
        query: str,
        limit: int = 5,
    ) -> RAGResponse:

        result = self.graph.invoke(
            {
                "query": query,
                "limit": limit,
            }
        )

        return RAGResponse(
            answer=result["answer"],
            sources=result["sources"],
            has_sufficient_context=result[
                "has_sufficient_context"
            ],
        )