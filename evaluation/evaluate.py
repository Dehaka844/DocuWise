from dotenv import load_dotenv

from app.graph.query_graph import QueryGraph

from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.qdrant_service import QdrantService
from app.services.retrieval_service import RetrievalService

from evaluation.metrics import (
    precision_at_k,
    recall_at_k,
    hit_at_k,
    context_detection_accuracy,
)

from evaluation.test_cases import TEST_CASES


load_dotenv()


TOP_K = 5


def run_evaluation():

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

    precision_scores = []

    recall_scores = []

    hit_scores = []

    context_scores = []

    for test_case in TEST_CASES:

        print()
        print("=" * 70)

        print(
            f"Evaluando: {test_case['name']}"
        )

        print(
            f"Pregunta: {test_case['query']}"
        )

        print("-" * 70)

        graph_result = graph.invoke(
            {
                "query": test_case["query"],
                "limit": TOP_K,
            }
        )

        retrieved_pages = [
            retrieval_result.metadata["page_number"]
            for retrieval_result in graph_result[
                "results"
            ]
        ]

        actual_has_context = graph_result[
            "has_sufficient_context"
        ]

        context_score = context_detection_accuracy(
            expected_has_context=(
                test_case["expected_has_context"]
            ),
            actual_has_context=actual_has_context,
        )

        context_scores.append(
            context_score
        )

        print(
            "Contexto esperado:",
            test_case["expected_has_context"],
        )

        print(
            "Contexto obtenido:",
            actual_has_context,
        )

        print(
            "Context Detection:",
            context_score,
        )

        print(
            "Páginas esperadas:",
            test_case["expected_pages"],
        )

        print(
            "Páginas recuperadas:",
            retrieved_pages,
        )

        if test_case["expected_has_context"]:

            expected_pages = (
                test_case["expected_pages"]
            )

            precision = precision_at_k(
                retrieved_pages=retrieved_pages,
                expected_pages=expected_pages,
                k=TOP_K,
            )

            recall = recall_at_k(
                retrieved_pages=retrieved_pages,
                expected_pages=expected_pages,
                k=TOP_K,
            )

            hit = hit_at_k(
                retrieved_pages=retrieved_pages,
                expected_pages=expected_pages,
                k=TOP_K,
            )

            precision_scores.append(
                precision
            )

            recall_scores.append(
                recall
            )

            hit_scores.append(
                hit
            )

            print(
                f"Precision@{TOP_K}:",
                round(
                    precision,
                    4,
                ),
            )

            print(
                f"Recall@{TOP_K}:",
                round(
                    recall,
                    4,
                ),
            )

            print(
                f"Hit@{TOP_K}:",
                round(
                    hit,
                    4,
                ),
            )

        print("-" * 70)

        print("Respuesta:")

        print(
            graph_result["answer"]
        )

    print()
    print("=" * 70)
    print("RESULTADOS FINALES")
    print("=" * 70)

    if precision_scores:

        average_precision = (
            sum(precision_scores)
            / len(precision_scores)
        )

        print(
            f"Precision@{TOP_K} media:",
            round(
                average_precision,
                4,
            ),
        )

    if recall_scores:

        average_recall = (
            sum(recall_scores)
            / len(recall_scores)
        )

        print(
            f"Recall@{TOP_K} medio:",
            round(
                average_recall,
                4,
            ),
        )

    if hit_scores:

        average_hit = (
            sum(hit_scores)
            / len(hit_scores)
        )

        print(
            f"Hit@{TOP_K} medio:",
            round(
                average_hit,
                4,
            ),
        )

    if context_scores:

        average_context_accuracy = (
            sum(context_scores)
            / len(context_scores)
        )

        print(
            "Context Detection Accuracy:",
            round(
                average_context_accuracy,
                4,
            ),
        )


if __name__ == "__main__":

    run_evaluation()