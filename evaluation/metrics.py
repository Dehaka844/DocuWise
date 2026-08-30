def precision_at_k(
    retrieved_pages: list[int],
    expected_pages: list[int],
    k: int,
) -> float:
    """
    Calcula Precision@K.

    Mide qué proporción de los K primeros resultados
    recuperados pertenece al conjunto de páginas esperadas.
    """

    if k <= 0:
        return 0.0

    if not retrieved_pages:
        return 0.0

    if not expected_pages:
        return 0.0

    top_k_pages = retrieved_pages[:k]

    relevant_results = sum(
        1
        for page in top_k_pages
        if page in expected_pages
    )

    return relevant_results / len(top_k_pages)


def recall_at_k(
    retrieved_pages: list[int],
    expected_pages: list[int],
    k: int,
) -> float:
    """
    Calcula Recall@K.

    Mide qué proporción de las páginas esperadas
    ha sido recuperada entre los K primeros resultados.

    Los resultados duplicados no aumentan el recall.
    """

    if k <= 0:
        return 0.0

    if not expected_pages:
        return 0.0

    if not retrieved_pages:
        return 0.0

    top_k_pages = retrieved_pages[:k]

    expected_set = set(expected_pages)

    retrieved_set = set(top_k_pages)

    relevant_retrieved = (
        expected_set & retrieved_set
    )

    return (
        len(relevant_retrieved)
        / len(expected_set)
    )


def hit_at_k(
    retrieved_pages: list[int],
    expected_pages: list[int],
    k: int,
) -> float:
    """
    Calcula Hit@K.

    Devuelve 1.0 si al menos una página esperada
    aparece entre los K primeros resultados.

    Devuelve 0.0 en caso contrario.
    """

    if k <= 0:
        return 0.0

    if not expected_pages:
        return 0.0

    if not retrieved_pages:
        return 0.0

    top_k_pages = retrieved_pages[:k]

    expected_set = set(expected_pages)

    retrieved_set = set(top_k_pages)

    return float(
        bool(
            expected_set & retrieved_set
        )
    )


def context_detection_accuracy(
    expected_has_context: bool,
    actual_has_context: bool,
) -> float:
    """
    Evalúa si la detección de contexto es correcta.
    """

    return float(
        expected_has_context
        == actual_has_context
    )