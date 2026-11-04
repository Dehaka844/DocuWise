# Resultados históricos de evaluación (V1)

> **Importante:** estos resultados pertenecen a una evaluación anterior de DocuWise sobre un documento de vacaciones, jornada y permisos que ya no forma parte del corpus ficticio actual. No son resultados de DocuWise 2.0 y no se han recalculado durante la actualización de documentación.

La evaluación automática definida en `evaluation/test_cases.py` produjo históricamente:

| Métrica | Resultado registrado |
|---|---:|
| Precision@5 media | 0.525 |
| Recall@5 medio | 0.9375 |
| Hit@5 medio | 1.0 |
| Context Detection Accuracy | 1.0 |

Las métricas miden recuperación por página y detección de contexto en el conjunto histórico. No miden por sí solas la corrección, completitud o fidelidad de las respuestas.

La evaluación manual de V2 está en [`../informes/`](../informes/) y usa un corpus distinto. Sus resultados no son directamente comparables con estas métricas.
