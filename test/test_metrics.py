from evaluation.metrics import (
    context_detection_accuracy,
    precision_at_k,
)


retrieved_pages = [
    5,
    19,
    7,
    18,
    6,
]

expected_pages = [
    5,
    6,
    7,
]


precision = precision_at_k(
    retrieved_pages=retrieved_pages,
    expected_pages=expected_pages,
    k=5,
)

print(
    "Precision@5:",
    precision,
)


accuracy_correct = context_detection_accuracy(
    expected_has_context=True,
    actual_has_context=True,
)

print(
    "Context detection correcto:",
    accuracy_correct,
)


accuracy_incorrect = context_detection_accuracy(
    expected_has_context=False,
    actual_has_context=True,
)

print(
    "Context detection incorrecto:",
    accuracy_incorrect,
)