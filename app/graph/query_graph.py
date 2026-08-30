from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService

from app.prompts.rag_prompt import (
    RAG_SYSTEM_PROMPT,
    RAG_USER_PROMPT,
)


class QueryState(TypedDict):

    query: str

    limit: int

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
            query=state["query"],
            limit=state["limit"],
        )

        return {
            "results": results,
        }


    def build(self):

        graph = StateGraph(QueryState)

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

        results = state["results"]

        if not results:

            return {
                "has_sufficient_context": False,
            }

        best_score = results[0].score

        return {
            "has_sufficient_context": (
                best_score >= self.score_threshold
            ),
        }
    
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

        context = "\n\n".join(
            result.content
            for result in state["results"]
        )

        user_prompt = RAG_USER_PROMPT.format(
            context=context,
            query=state["query"],
        )

        answer = self.llm_service.generate(
            system_prompt=RAG_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        sources = []

        seen_sources = set()

        for result in state["results"]:

            filename = result.metadata["filename"]

            page_number = result.metadata["page_number"]

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