import logging
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService
from app.exceptions.llm_exception import LLMServiceError

from app.prompts.rag_prompt import (
    RAG_USER_PROMPT,
    build_rag_system_prompt,
)


logger = logging.getLogger(__name__)


class QueryState(TypedDict):

    query: str

    search_query: str

    limit: int

    conversation_history: list

    user_id: int

    departments: list[str]

    is_admin: bool

    results: list

    has_sufficient_context: bool

    answer: str

    sources: list


class QueryGraph:

    def __init__(
        self,
        retrieval_service: RetrievalService,
        llm_service: LLMService,
        score_threshold: float = 0.4,
    ):
        self.retrieval_service = retrieval_service

        self.llm_service = llm_service

        self.score_threshold = score_threshold


    def retrieve(
        self,
        state: QueryState,
    ) -> dict:

        results = self.retrieval_service.retrieve(
            query=state.get("search_query", state["query"]),
            limit=state["limit"],
            user_id=state.get("user_id"),
            departments=state.get("departments", []),
            is_admin=state.get("is_admin", False),
        )

        return {
            "results": results,
        }

    def rewrite_query(
        self,
        state: QueryState,
    ) -> dict:
        query = state["query"]
        conversation_history = state.get(
            "conversation_history",
            [],
        )

        if not conversation_history:
            return {"search_query": query}

        try:
            search_query = self.llm_service.rewrite_query(
                query=query,
                conversation_history=conversation_history,
            )
        except LLMServiceError:
            logger.warning(
                "No se pudo reformular la consulta; se usará la pregunta original.",
                exc_info=True,
            )
            search_query = query

        return {"search_query": search_query}


    def build(self):

        graph = StateGraph(QueryState)

        graph.add_node(
            "rewrite_query",
            self.rewrite_query,
        )

        graph.add_node(
            "retrieve",
            self.retrieve,
        )

        graph.add_node(
            "check_context",
            self.check_context,
        )

        graph.add_node(
            "generate",
            self.generate,
        )

        graph.add_node(
            "no_context",
            self.no_context,
        )

        graph.add_edge(
            START,
            "rewrite_query",
        )

        graph.add_edge(
            "rewrite_query",
            "retrieve",
        )

        graph.add_edge(
            "retrieve",
            "check_context",
        )

        graph.add_conditional_edges(
            "check_context",
            self.route_context,
            {
                "generate": "generate",
                "no_context": "no_context",
            },
        )

        graph.add_edge(
            "generate",
            END,
        )

        graph.add_edge(
            "no_context",
            END,
        )

        return graph.compile()

    def check_context(
        self,
        state: QueryState,
    ) -> dict:

        relevant_results = self._relevant_results(
            state["results"]
        )

        return {
            "has_sufficient_context": bool(relevant_results),
        }

    def _relevant_results(self, results: list) -> list:
        return [
            result
            for result in results
            if result.score >= self.score_threshold
        ]
    
    def route_context(
        self,
        state: QueryState,
    ) -> str:

        if state["has_sufficient_context"]:

            return "generate"

        return "no_context"

    def no_context(
        self,
        state: QueryState,
    ) -> dict:

        return {
            "answer": (
                "No he encontrado información "
                "suficientemente relevante en los documentos "
                "para responder a esta pregunta."
            ),
            "sources": [],
        }

    def generate(
        self,
        state: QueryState,
    ) -> dict:

        relevant_results = self._relevant_results(
            state["results"]
        )

        context = "\n\n".join(
            result.content
            for result in relevant_results
        )

        relevant_domains = set()
        for result in relevant_results:
            result_domains = result.metadata.get("domains", [])
            if isinstance(result_domains, str):
                result_domains = [result_domains]

            if isinstance(result_domains, list):
                relevant_domains.update(
                    domain
                    for domain in result_domains
                    if isinstance(domain, str)
                )

        system_prompt = build_rag_system_prompt(
            sorted(relevant_domains)
        )

        conversation_history = "\n".join(
            f"{message.role}: {message.content}"
            for message in state.get("conversation_history", [])
        )

        user_prompt = RAG_USER_PROMPT.format(
            conversation_history=conversation_history,
            context=context,
            query=state["query"],
        )

        answer = self.llm_service.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        sources = []

        seen_sources = set()

        for result in relevant_results:

            filename = result.metadata["filename"]

            page_number = (
                result.metadata.get("page_number")
                if result.metadata.get("source_type") == "pdf"
                else None
            )

            source_key = (
                filename,
                page_number,
            )

            if source_key not in seen_sources:

                seen_sources.add(source_key)

                sources.append(
                    {
                        "filename": filename,
                        "page_number": page_number,
                    }
                )

        return {
            "answer": answer,
            "sources": sources,
        }
